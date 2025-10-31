const tf = require('@tensorflow/tfjs-node');
const brain = require('brain.js');
const stats = require('simple-statistics');
const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');

class UniversalPredictionEngine extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      modelType: config.modelType || 'auto',
      learningRate: config.learningRate || 0.01,
      epochs: config.epochs || 100,
      batchSize: config.batchSize || 32,
      ...config
    };

    this.models = new Map();
    this.predictions = new Map();
    this.knowledgeGraph = new Map();
    this.patterns = [];
  }

  async trainModel(modelName, data, config = {}) {
    const modelConfig = { ...this.config, ...config };
    const modelId = uuidv4();

    try {
      const model = await this.createModel(data, modelConfig);

      this.models.set(modelName, {
        id: modelId,
        model,
        type: modelConfig.modelType,
        trainedAt: new Date(),
        config: modelConfig,
        metrics: await this.evaluateModel(model, data)
      });

      this.updateKnowledgeGraph(modelName, data);

      this.emit('model:trained', {
        modelName,
        modelId,
        metrics: this.models.get(modelName).metrics
      });

      return {
        modelId,
        status: 'trained',
        metrics: this.models.get(modelName).metrics
      };
    } catch (error) {
      this.emit('model:error', {
        modelName,
        error: error.message
      });
      throw error;
    }
  }

  async createModel(data, config) {
    const modelType = config.modelType === 'auto'
      ? this.detectModelType(data)
      : config.modelType;

    switch (modelType) {
      case 'neural':
        return this.createNeuralNetwork(data, config);
      case 'lstm':
        return this.createLSTM(data, config);
      case 'linear':
        return this.createLinearRegression(data, config);
      case 'classification':
        return this.createClassifier(data, config);
      default:
        return this.createNeuralNetwork(data, config);
    }
  }

  createNeuralNetwork(data, config) {
    const net = new brain.NeuralNetwork({
      hiddenLayers: config.hiddenLayers || [10, 10],
      activation: config.activation || 'sigmoid',
      learningRate: config.learningRate
    });

    const trainingData = this.prepareTrainingData(data);
    net.train(trainingData, {
      iterations: config.epochs,
      errorThresh: 0.005,
      log: false,
      logPeriod: 10
    });

    return net;
  }

  async createLSTM(data, config) {
    const model = tf.sequential({
      layers: [
        tf.layers.lstm({
          units: 50,
          returnSequences: true,
          inputShape: [data.sequenceLength || 10, data.features || 1]
        }),
        tf.layers.lstm({
          units: 50,
          returnSequences: false
        }),
        tf.layers.dense({
          units: 1
        })
      ]
    });

    model.compile({
      optimizer: tf.train.adam(config.learningRate),
      loss: 'meanSquaredError',
      metrics: ['mae']
    });

    return model;
  }

  createLinearRegression(data, config) {
    const regression = {
      type: 'linear',
      coefficients: null,
      predict: function(input) {
        if (!this.coefficients) return null;
        return stats.linearRegression(input, this.coefficients);
      }
    };

    const x = data.map(d => d.input);
    const y = data.map(d => d.output);
    regression.coefficients = stats.linearRegression([x, y]);

    return regression;
  }

  createClassifier(data, config) {
    const net = new brain.recurrent.LSTM({
      hiddenLayers: config.hiddenLayers || [20],
      activation: config.activation || 'tanh'
    });

    const trainingData = data.map(item => ({
      input: item.input,
      output: item.output
    }));

    net.train(trainingData, {
      iterations: config.epochs,
      errorThresh: 0.011
    });

    return net;
  }

  async predict(modelName, input, options = {}) {
    const modelData = this.models.get(modelName);
    if (!modelData) {
      throw new Error(`Model ${modelName} not found`);
    }

    const predictionId = uuidv4();

    try {
      let prediction;
      const { model, type } = modelData;

      if (type === 'neural' || type === 'classification') {
        prediction = model.run(input);
      } else if (type === 'lstm') {
        const tensor = tf.tensor3d([input]);
        const output = model.predict(tensor);
        prediction = await output.array();
        tensor.dispose();
        output.dispose();
      } else if (type === 'linear') {
        prediction = model.predict(input);
      } else {
        prediction = model.run ? model.run(input) : model.predict(input);
      }

      const result = {
        id: predictionId,
        modelName,
        input,
        prediction,
        confidence: this.calculateConfidence(prediction, modelData),
        timestamp: new Date()
      };

      this.predictions.set(predictionId, result);

      if (options.explain) {
        result.explanation = this.explainPrediction(modelName, input, prediction);
      }

      this.detectPatterns(modelName, input, prediction);

      this.emit('prediction:made', result);
      return result;
    } catch (error) {
      this.emit('prediction:error', {
        modelName,
        error: error.message
      });
      throw error;
    }
  }

  async batchPredict(modelName, inputs) {
    const results = [];
    for (const input of inputs) {
      try {
        const result = await this.predict(modelName, input);
        results.push(result);
      } catch (error) {
        results.push({
          input,
          error: error.message
        });
      }
    }
    return results;
  }

  detectModelType(data) {
    if (!data || data.length === 0) return 'neural';

    const sample = data[0];

    if (sample.sequence) return 'lstm';
    if (sample.text) return 'classification';
    if (sample.continuous) return 'linear';

    return 'neural';
  }

  prepareTrainingData(data) {
    if (Array.isArray(data) && data.length > 0) {
      if (data[0].input && data[0].output) {
        return data;
      }
    }

    return data.map(item => ({
      input: this.normalizeInput(item.input || item),
      output: this.normalizeOutput(item.output || item)
    }));
  }

  normalizeInput(input) {
    if (typeof input === 'number') return [input];
    if (Array.isArray(input)) return input;
    if (typeof input === 'object') return Object.values(input);
    return [0];
  }

  normalizeOutput(output) {
    if (typeof output === 'number') return [output];
    if (Array.isArray(output)) return output;
    if (typeof output === 'object') return Object.values(output);
    return [0];
  }

  calculateConfidence(prediction, modelData) {
    if (!modelData.metrics) return 0.5;

    const accuracy = modelData.metrics.accuracy || 0.5;
    const variance = this.calculateVariance(prediction);

    return Math.min(1, accuracy * (1 - variance));
  }

  calculateVariance(prediction) {
    if (Array.isArray(prediction)) {
      return stats.variance(prediction) || 0;
    }
    return 0;
  }

  async evaluateModel(model, testData) {
    let correct = 0;
    let total = testData.length;
    let totalError = 0;

    for (const item of testData) {
      try {
        const prediction = model.run
          ? model.run(item.input)
          : await model.predict(item.input);

        const error = this.calculateError(prediction, item.output);
        totalError += error;

        if (error < 0.1) correct++;
      } catch (e) {
        total--;
      }
    }

    return {
      accuracy: total > 0 ? correct / total : 0,
      averageError: total > 0 ? totalError / total : 1,
      samplesEvaluated: total
    };
  }

  calculateError(predicted, actual) {
    if (Array.isArray(predicted) && Array.isArray(actual)) {
      return stats.rootMeanSquare(
        predicted.map((p, i) => p - (actual[i] || 0))
      );
    }
    return Math.abs(predicted - actual);
  }

  updateKnowledgeGraph(modelName, data) {
    const nodes = new Set();
    const edges = [];

    data.forEach(item => {
      const inputKeys = Object.keys(item.input || {});
      const outputKeys = Object.keys(item.output || {});

      inputKeys.forEach(key => {
        nodes.add(key);
        outputKeys.forEach(outKey => {
          edges.push({ from: key, to: outKey, model: modelName });
        });
      });

      outputKeys.forEach(key => nodes.add(key));
    });

    this.knowledgeGraph.set(modelName, {
      nodes: Array.from(nodes),
      edges,
      updatedAt: new Date()
    });
  }

  detectPatterns(modelName, input, prediction) {
    const pattern = {
      modelName,
      input,
      prediction,
      timestamp: new Date()
    };

    this.patterns.push(pattern);

    if (this.patterns.length > 1000) {
      this.patterns = this.patterns.slice(-500);
    }

    const recentPatterns = this.patterns.slice(-10);
    const trend = this.analyzeTrend(recentPatterns);

    if (trend.significant) {
      this.emit('pattern:detected', {
        modelName,
        trend,
        patterns: recentPatterns
      });
    }
  }

  analyzeTrend(patterns) {
    if (patterns.length < 3) {
      return { significant: false };
    }

    const values = patterns.map(p =>
      Array.isArray(p.prediction) ? p.prediction[0] : p.prediction
    );

    const slope = stats.linearRegressionLine(
      stats.linearRegression(patterns.map((_, i) => [i, values[i]]))
    );

    return {
      significant: Math.abs(slope(1) - slope(0)) > 0.1,
      direction: slope(1) > slope(0) ? 'increasing' : 'decreasing',
      strength: Math.abs(slope(1) - slope(0))
    };
  }

  explainPrediction(modelName, input, prediction) {
    const modelData = this.models.get(modelName);
    const knowledge = this.knowledgeGraph.get(modelName);

    return {
      model: modelName,
      modelType: modelData.type,
      inputFeatures: Object.keys(input),
      predictionConfidence: this.calculateConfidence(prediction, modelData),
      relatedNodes: knowledge ? knowledge.nodes : [],
      trainingMetrics: modelData.metrics
    };
  }

  getModel(modelName) {
    return this.models.get(modelName);
  }

  getAllModels() {
    return Array.from(this.models.entries()).map(([name, data]) => ({
      name,
      ...data,
      model: undefined
    }));
  }

  deleteModel(modelName) {
    if (this.models.has(modelName)) {
      this.models.delete(modelName);
      this.knowledgeGraph.delete(modelName);
      this.emit('model:deleted', { modelName });
      return { status: 'deleted' };
    }
    return { status: 'not_found' };
  }

  getPatterns(modelName = null) {
    if (modelName) {
      return this.patterns.filter(p => p.modelName === modelName);
    }
    return this.patterns;
  }

  getPredictionHistory(limit = 10) {
    const predictions = Array.from(this.predictions.values());
    return predictions.slice(-limit);
  }
}

const express = require('express');
const app = express();
app.use(express.json());

const engine = new UniversalPredictionEngine();

app.post('/train/:model', async (req, res) => {
  try {
    const result = await engine.trainModel(
      req.params.model,
      req.body.data,
      req.body.config
    );
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/predict/:model', async (req, res) => {
  try {
    const result = await engine.predict(
      req.params.model,
      req.body.input,
      req.body.options
    );
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/batch-predict/:model', async (req, res) => {
  try {
    const results = await engine.batchPredict(
      req.params.model,
      req.body.inputs
    );
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/models', (req, res) => {
  res.json(engine.getAllModels());
});

app.get('/model/:name', (req, res) => {
  const model = engine.getModel(req.params.name);
  if (model) {
    res.json({ ...model, model: undefined });
  } else {
    res.status(404).json({ error: 'Model not found' });
  }
});

app.delete('/model/:name', (req, res) => {
  const result = engine.deleteModel(req.params.name);
  res.json(result);
});

app.get('/patterns', (req, res) => {
  const patterns = engine.getPatterns(req.query.model);
  res.json(patterns);
});

app.get('/history', (req, res) => {
  const history = engine.getPredictionHistory(req.query.limit || 10);
  res.json(history);
});

const PORT = process.env.PORT || 3005;
app.listen(PORT, () => {
  console.log(`Prediction Engine running on port ${PORT}`);
});

module.exports = UniversalPredictionEngine;