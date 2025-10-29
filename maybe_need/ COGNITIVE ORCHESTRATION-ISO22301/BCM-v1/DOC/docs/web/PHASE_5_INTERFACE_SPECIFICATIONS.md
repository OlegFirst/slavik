# ЭТАП 5: Intelligence & Analytics - Interface Specifications

## 🎯 ТЗ для команды интерфейсов - ЭТАП 5

### **Затронутые модули с новым функционалом:**

```yaml
bcm_reporting:     ✅ MAJOR ENHANCEMENT - Analytics & AI Insights
bcm_community:     ✅ ENHANCED - Knowledge Base functionality
Scenario Orchestrator: ✅ ENHANCED - Experience accumulation API
Grafana:          ✅ INTEGRATION - Technical monitoring dashboards
```

---

## 📊 **ИНТЕРФЕЙС 1: Analytics Dashboard (Odoo bcm_reporting)**

### **Location**: Odoo BCM Platform - bcm_reporting module

### **NEW Views Required:**

#### **1.1: Analytics Dashboard Form View**
```xml
<!-- NEW: Enhanced Analytics Dashboard Interface -->
<record id="view_bcm_analytics_dashboard_form" model="ir.ui.view">
    <field name="name">bcm.analytics.dashboard.form</field>
    <field name="model">bcm.analytics.dashboard</field>
    <field name="arch" type="xml">
        <form string="BCM Analytics Dashboard">
            <header>
                <button name="action_refresh_analytics" type="object"
                        string="🔄 Refresh Data" class="btn-primary"/>

                <field name="last_updated" widget="badge" readonly="1"
                       decoration-success="True"/>
            </header>

            <sheet>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Dashboard Name"/></h1>
                </div>

                <group>
                    <group string="Dashboard Configuration">
                        <field name="dashboard_type" widget="radio"/>
                        <field name="description"/>
                    </group>
                    <group string="Auto-Refresh Settings">
                        <field name="auto_refresh"/>
                        <field name="refresh_interval_minutes"
                               attrs="{'invisible': [('auto_refresh', '=', False)]}"/>
                    </group>
                </group>

                <!-- Analytics Data Visualization -->
                <div class="analytics-visualization">
                    <h3>📊 Analytics Data</h3>

                    <!-- Executive Dashboard -->
                    <div class="dashboard-content executive-dashboard"
                         attrs="{'invisible': [('dashboard_type', '!=', 'executive')]}">

                        <div class="row">
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-number">
                                        <field name="total_scenarios" readonly="1"/>
                                    </div>
                                    <div class="metric-label">Total Scenarios</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-number">
                                        <field name="total_exercises" readonly="1"/>
                                    </div>
                                    <div class="metric-label">Total Exercises</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-number">
                                        <field name="ai_generated_scenarios" readonly="1"/>
                                    </div>
                                    <div class="metric-label">AI Scenarios</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-number">
                                        <field name="platform_effectiveness" readonly="1"/>%
                                    </div>
                                    <div class="metric-label">Platform Effectiveness</div>
                                </div>
                            </div>
                        </div>

                        <!-- Executive Charts -->
                        <div class="executive-charts mt-4">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="chart-container">
                                        <h6>Exercise Performance Trend</h6>
                                        <field name="exercise_performance_chart" widget="dashboard_chart"/>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="chart-container">
                                        <h6>Scenario Effectiveness Distribution</h6>
                                        <field name="scenario_effectiveness_chart" widget="dashboard_chart"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- AI Insights Dashboard -->
                    <div class="dashboard-content ai-insights-dashboard"
                         attrs="{'invisible': [('dashboard_type', '!=', 'ai_insights')]}">

                        <div class="ai-learning-summary">
                            <h4>🤖 AI Learning Summary</h4>

                            <div class="learning-metrics">
                                <div class="metric-grid">
                                    <div class="metric-item">
                                        <span class="metric-value">
                                            <field name="scenarios_with_learning_data" readonly="1"/>
                                        </span>
                                        <span class="metric-label">Scenarios with Learning Data</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-value">
                                            <field name="avg_platform_effectiveness" readonly="1"/>
                                        </span>
                                        <span class="metric-label">Avg Platform Effectiveness</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-value">
                                            <field name="total_exercises_completed" readonly="1"/>
                                        </span>
                                        <span class="metric-label">Completed Exercises</span>
                                    </div>
                                </div>
                            </div>

                            <!-- AI Recommendations -->
                            <div class="ai-recommendations mt-4">
                                <h5>💡 AI Improvement Recommendations</h5>
                                <field name="ai_recommendations_list" widget="ai_recommendations"/>
                            </div>

                            <!-- Top Performing Scenarios -->
                            <div class="top-scenarios mt-4">
                                <h5>⭐ Top Performing Scenarios</h5>
                                <field name="top_scenarios_list" widget="scenario_ranking"/>
                            </div>
                        </div>
                    </div>

                    <!-- Raw Analytics Data (for developers) -->
                    <div class="raw-analytics-data mt-4">
                        <field name="analytics_data" widget="ace" options="{'mode': 'json'}"
                               attrs="{'invisible': [('analytics_data', '=', False)]}"/>
                    </div>
                </div>
            </sheet>

            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

#### **1.2: Analytics Dashboard Kanban View**
```xml
<!-- NEW: Analytics Dashboard Overview -->
<record id="view_bcm_analytics_dashboard_kanban" model="ir.ui.view">
    <field name="name">bcm.analytics.dashboard.kanban</field>
    <field name="model">bcm.analytics.dashboard</field>
    <field name="arch" type="xml">
        <kanban class="o_kanban_dashboard">
            <field name="name"/>
            <field name="dashboard_type"/>
            <field name="last_updated"/>
            <field name="analytics_data"/>

            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card analytics-dashboard-card">
                        <div class="oe_kanban_content">
                            <!-- Dashboard Header -->
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <i t-attf-class="#{getDashboardIcon(record.dashboard_type.raw_value)} mr-2"></i>
                                        <t t-esc="record.name.value"/>
                                    </strong>
                                    <div class="text-muted">
                                        <t t-esc="record.dashboard_type.value"/>
                                    </div>
                                </div>
                            </div>

                            <!-- Quick Metrics Preview -->
                            <div class="o_kanban_record_body">
                                <div class="dashboard-preview" t-if="record.analytics_data.raw_value">
                                    <div class="preview-metrics">
                                        <!-- Metrics preview will be populated by JavaScript -->
                                        <div class="metrics-placeholder">
                                            <i class="fas fa-chart-line text-primary"></i>
                                            Click to view analytics
                                        </div>
                                    </div>
                                </div>

                                <div class="no-data-message" t-if="!record.analytics_data.raw_value">
                                    <p class="text-muted">No analytics data yet</p>
                                    <button class="btn btn-sm btn-primary refresh-btn">
                                        <i class="fas fa-sync"></i> Generate Data
                                    </button>
                                </div>
                            </div>

                            <!-- Dashboard Actions -->
                            <div class="o_kanban_record_bottom">
                                <div class="oe_kanban_bottom_left">
                                    <small class="text-muted">
                                        Updated: <t t-esc="record.last_updated.value"/>
                                    </small>
                                </div>
                                <div class="oe_kanban_bottom_right">
                                    <a type="object" name="action_refresh_analytics" class="btn btn-sm btn-primary">
                                        <i class="fas fa-sync"></i> Refresh
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

## 📚 **ИНТЕРФЕЙС 2: Knowledge Base (Odoo bcm_community)**

### **NEW Odoo Views:**

#### **2.1: Knowledge Article Management**
```xml
<!-- NEW: Knowledge Article Form View -->
<record id="view_bcm_knowledge_article_form" model="ir.ui.view">
    <field name="name">bcm.knowledge.article.form</field>
    <field name="model">bcm.knowledge.article</field>
    <field name="arch" type="xml">
        <form string="Knowledge Article">
            <header>
                <button name="action_regenerate_with_ai" type="object"
                        string="🤖 Regenerate with AI" class="btn-primary"
                        attrs="{'invisible': [('article_type', '!=', 'ai_generated')]}"/>

                <button name="website_publish_button" type="object"
                        string="📢 Publish to Website" class="btn-success"
                        attrs="{'invisible': [('is_published', '=', True)]}"/>

                <field name="is_published" widget="boolean_toggle"/>
            </header>

            <sheet>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Article Title"/></h1>
                </div>

                <group>
                    <group string="Article Information">
                        <field name="category"/>
                        <field name="article_type" readonly="1"/>
                        <field name="usefulness_score" readonly="1"/>
                    </group>
                    <group string="Source Information">
                        <field name="source_exercise_id" readonly="1"/>
                        <field name="source_scenario_id" readonly="1"/>
                        <field name="source_forum_topic_id" readonly="1"/>
                    </group>
                </group>

                <!-- Article Content -->
                <group string="Content">
                    <field name="summary" placeholder="Brief article summary..."/>
                    <field name="content" widget="html" options="{'height': 400}"/>
                </group>

                <!-- AI Generation (if applicable) -->
                <group string="AI Generation" attrs="{'invisible': [('article_type', '!=', 'ai_generated')]}">
                    <field name="ai_prompt" placeholder="AI generation prompt used..."/>
                    <field name="ai_confidence" readonly="1"/>
                </group>

                <!-- Organization -->
                <group string="Organization & Relationships">
                    <field name="tags" widget="many2many_tags"/>
                    <field name="iso_clauses" widget="many2many_tags"/>
                    <field name="sequence"/>
                </group>

                <!-- Related Content -->
                <group string="Related Content">
                    <field name="related_scenarios" widget="many2many_tags"/>
                    <field name="related_templates" widget="many2many_tags"/>
                    <field name="parent_article_id"/>
                </group>

                <!-- Analytics -->
                <group string="Analytics" groups="bcm_core.group_bcm_manager">
                    <group>
                        <field name="view_count" readonly="1"/>
                        <field name="bookmark_count" readonly="1"/>
                    </group>
                    <group>
                        <field name="feedback_count" readonly="1"/>
                        <field name="usefulness_score" readonly="1"/>
                    </group>
                </group>

                <!-- Sub-articles -->
                <div class="sub-articles" attrs="{'invisible': [('child_article_ids', '=', [])]}">
                    <h3>📄 Sub-articles</h3>
                    <field name="child_article_ids" mode="tree">
                        <tree>
                            <field name="name"/>
                            <field name="category"/>
                            <field name="usefulness_score"/>
                            <field name="is_published"/>
                        </tree>
                    </field>
                </div>
            </sheet>

            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

#### **2.2: Knowledge Base Portal (Website)**
```html
<!-- NEW: Website Knowledge Base Template -->
<template id="knowledge_base_portal" name="BCM Knowledge Base Portal">
    <t t-call="website.layout">
        <div id="wrap" class="knowledge-base-portal">
            <!-- Hero Section -->
            <section class="hero-section bg-primary text-white py-5">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-8 offset-lg-2 text-center">
                            <h1>📚 BCM Knowledge Base</h1>
                            <p class="lead">AI-powered knowledge repository for Business Continuity Management</p>

                            <!-- Search Bar -->
                            <div class="search-container mt-4">
                                <div class="input-group input-group-lg">
                                    <input type="text" id="knowledge-search"
                                           class="form-control"
                                           placeholder="Search knowledge articles, best practices, procedures..."/>
                                    <div class="input-group-append">
                                        <button class="btn btn-light" onclick="searchKnowledge()">
                                            <i class="fas fa-search"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Quick Stats -->
            <section class="stats-section py-4 bg-light">
                <div class="container">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <div class="stat-item">
                                <h3 class="stat-number"><t t-esc="total_articles"/></h3>
                                <p class="stat-label">Knowledge Articles</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-item">
                                <h3 class="stat-number"><t t-esc="ai_generated_articles"/></h3>
                                <p class="stat-label">AI Generated</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-item">
                                <h3 class="stat-number"><t t-esc="exercise_derived_articles"/></h3>
                                <p class="stat-label">From Exercises</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-item">
                                <h3 class="stat-number"><t t-esc="community_articles"/></h3>
                                <p class="stat-label">Community Created</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Main Content -->
            <section class="main-content py-5">
                <div class="container">
                    <div class="row">
                        <!-- Sidebar - Categories & Filters -->
                        <div class="col-md-3">
                            <div class="knowledge-sidebar">
                                <!-- Categories -->
                                <div class="category-section mb-4">
                                    <h5>📂 Categories</h5>
                                    <div class="category-list">
                                        <t t-foreach="categories" t-as="category">
                                            <a t-attf-href="/bcm/community/knowledge?category=#{category.code}"
                                               class="category-link">
                                                <i t-attf-class="#{category.icon}"></i>
                                                <t t-esc="category.name"/>
                                                <span class="article-count">(<t t-esc="category.article_count"/>)</span>
                                            </a>
                                        </t>
                                    </div>
                                </div>

                                <!-- Popular Tags -->
                                <div class="tags-section mb-4">
                                    <h5>🏷️ Popular Tags</h5>
                                    <div class="tag-cloud">
                                        <t t-foreach="popular_tags" t-as="tag">
                                            <span class="tag-pill" onclick="filterByTag('{{ tag.name }}')">
                                                <t t-esc="tag.name"/> (<t t-esc="tag.article_count"/>)
                                            </span>
                                        </t>
                                    </div>
                                </div>

                                <!-- ISO 22301 Clauses -->
                                <div class="iso-clauses-section">
                                    <h5>📋 ISO 22301 Clauses</h5>
                                    <div class="iso-list">
                                        <t t-foreach="iso_clauses" t-as="clause">
                                            <a t-attf-href="/bcm/community/knowledge?iso_clause=#{clause.name}"
                                               class="iso-link">
                                                <t t-esc="clause.name"/>: <t t-esc="clause.title"/>
                                                <span class="article-count">(<t t-esc="clause.article_count"/>)</span>
                                            </a>
                                        </t>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Main Content Area -->
                        <div class="col-md-9">
                            <!-- Featured Articles -->
                            <div class="featured-articles mb-5">
                                <h4>⭐ Featured Articles</h4>
                                <div class="row">
                                    <t t-foreach="featured_articles" t-as="article">
                                        <div class="col-md-6 mb-3">
                                            <div class="article-card featured">
                                                <div class="card-header">
                                                    <span class="category-badge" t-attf-class="badge-#{article.category}">
                                                        <t t-esc="article.category"/>
                                                    </span>
                                                    <span t-if="article.article_type == 'ai_generated'"
                                                          class="ai-badge">
                                                        <i class="fas fa-robot"></i> AI
                                                    </span>
                                                </div>
                                                <div class="card-body">
                                                    <h5 class="card-title">
                                                        <t t-esc="article.name"/>
                                                    </h5>
                                                    <p class="card-text">
                                                        <t t-esc="article.summary"/>
                                                    </p>
                                                    <div class="article-meta">
                                                        <small class="text-muted">
                                                            <i class="fas fa-eye"></i> <t t-esc="article.view_count"/> views
                                                            <span class="mx-2">•</span>
                                                            <i class="fas fa-star"></i> <t t-esc="article.usefulness_score"/> rating
                                                        </small>
                                                    </div>
                                                </div>
                                                <div class="card-footer">
                                                    <a t-attf-href="/bcm/community/knowledge/article/#{article.id}"
                                                       class="btn btn-primary btn-sm">
                                                        <i class="fas fa-arrow-right"></i> Read Article
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </t>
                                </div>
                            </div>

                            <!-- Recent Articles -->
                            <div class="recent-articles">
                                <h4>🕒 Recently Added</h4>
                                <div class="article-list">
                                    <t t-foreach="recent_articles" t-as="article">
                                        <div class="article-item">
                                            <div class="article-info">
                                                <h6>
                                                    <a t-attf-href="/bcm/community/knowledge/article/#{article.id}">
                                                        <t t-esc="article.name"/>
                                                    </a>
                                                </h6>
                                                <p class="article-summary"><t t-esc="article.summary"/></p>
                                                <div class="article-meta">
                                                    <span class="badge" t-attf-class="badge-#{article.category}">
                                                        <t t-esc="article.category"/>
                                                    </span>
                                                    <small class="text-muted ml-2">
                                                        Added <t t-esc="article.create_date"/>
                                                    </small>
                                                </div>
                                            </div>
                                            <div class="article-actions">
                                                <button class="btn btn-sm btn-outline-primary"
                                                        onclick="bookmarkArticle({{ article.id }})">
                                                    <i class="fas fa-bookmark"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </t>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- JavaScript for Knowledge Base functionality -->
        <script type="text/javascript">
            function searchKnowledge() {
                const query = document.getElementById('knowledge-search').value;
                if (query.trim()) {
                    window.location.href = `/bcm/community/knowledge/search?q=${encodeURIComponent(query)}`;
                }
            }

            function filterByTag(tagName) {
                window.location.href = `/bcm/community/knowledge?tag=${encodeURIComponent(tagName)}`;
            }

            function bookmarkArticle(articleId) {
                fetch(`/bcm/community/api/knowledge/article/${articleId}/bookmark`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update bookmark count visually
                        showNotification('Article bookmarked!', 'success');
                    }
                });
            }

            // Auto-complete search
            document.getElementById('knowledge-search').addEventListener('input', function(e) {
                const query = e.target.value;
                if (query.length > 2) {
                    // Implement auto-complete functionality
                    // Could integrate with Odoo search API
                }
            });
        </script>
    </t>
</template>
```

---

## 📱 **ИНТЕРФЕЙС 3: Learning Analytics (Vue.js)**

### **Location**: Web Portal v2 - `/frontend/web_portal_v2/src/components/analytics/`

#### **3.1: LearningAnalyticsDashboard.vue**
```vue
<template>
  <div class="learning-analytics-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <h2><i class="fas fa-brain"></i> AI Learning Analytics</h2>
      <div class="refresh-controls">
        <span class="last-update">Last updated: {{ lastUpdated }}</span>
        <button @click="refreshAnalytics" class="btn btn-primary">
          <i class="fas fa-sync" :class="{ 'fa-spin': isRefreshing }"></i>
          {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Key Metrics Overview -->
    <div class="metrics-overview">
      <div class="row">
        <div class="col-md-3">
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-file-text text-primary"></i>
            </div>
            <div class="metric-content">
              <h3>{{ learningData.total_scenarios_with_data || 0 }}</h3>
              <p>Scenarios with Learning Data</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-chart-line text-success"></i>
            </div>
            <div class="metric-content">
              <h3>{{ learningData.avg_platform_effectiveness || 0 }}%</h3>
              <p>Platform Effectiveness</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-dumbbell text-info"></i>
            </div>
            <div class="metric-content">
              <h3>{{ learningData.total_exercises_completed || 0 }}</h3>
              <p>Exercises Completed</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-lightbulb text-warning"></i>
            </div>
            <div class="metric-content">
              <h3>{{ improvementRecommendations.length || 0 }}</h3>
              <p>AI Recommendations</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Charts -->
    <div class="analytics-charts">
      <div class="row">
        <!-- Effectiveness Trend Chart -->
        <div class="col-md-6">
          <div class="chart-card">
            <div class="chart-header">
              <h5><i class="fas fa-chart-line"></i> Effectiveness Trend</h5>
            </div>
            <div class="chart-body">
              <Line :data="effectivenessTrendData" :options="chartOptions" />
            </div>
          </div>
        </div>

        <!-- Scenario Performance Distribution -->
        <div class="col-md-6">
          <div class="chart-card">
            <div class="chart-header">
              <h5><i class="fas fa-pie-chart"></i> Scenario Performance</h5>
            </div>
            <div class="chart-body">
              <Doughnut :data="scenarioPerformanceData" :options="chartOptions" />
            </div>
          </div>
        </div>
      </div>

      <div class="row mt-4">
        <!-- Exercise Type Effectiveness -->
        <div class="col-md-6">
          <div class="chart-card">
            <div class="chart-header">
              <h5><i class="fas fa-bar-chart"></i> Exercise Type Effectiveness</h5>
            </div>
            <div class="chart-body">
              <Bar :data="exerciseTypeData" :options="chartOptions" />
            </div>
          </div>
        </div>

        <!-- AI vs Manual Scenarios -->
        <div class="col-md-6">
          <div class="chart-card">
            <div class="chart-header">
              <h5><i class="fas fa-robot"></i> AI vs Manual Scenarios</h5>
            </div>
            <div class="chart-body">
              <Bar :data="aiVsManualData" :options="chartOptions" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Performing Scenarios -->
    <div class="top-scenarios-section mt-5">
      <div class="section-header">
        <h4><i class="fas fa-trophy"></i> Top Performing Scenarios</h4>
        <button @click="viewAllScenarios" class="btn btn-outline-primary">
          View All Scenarios →
        </button>
      </div>

      <div class="scenarios-grid">
        <div v-for="scenario in topScenarios" :key="scenario.id"
             class="scenario-performance-card">
          <div class="card-header">
            <h6>{{ scenario.title }}</h6>
            <div class="performance-badges">
              <span class="badge badge-success">
                {{ scenario.avg_rating }}/10 Rating
              </span>
              <span class="badge badge-info">
                {{ scenario.exercise_count }} Uses
              </span>
              <span v-if="scenario.ai_generated" class="badge badge-primary">
                <i class="fas fa-robot"></i> AI
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="performance-metrics">
              <div class="metric-row">
                <span>Category:</span>
                <span>{{ scenario.category }}</span>
              </div>
              <div class="metric-row">
                <span>Effectiveness:</span>
                <div class="effectiveness-bar">
                  <div class="progress">
                    <div class="progress-bar bg-success"
                         :style="{ width: scenario.effectiveness + '%' }">
                    </div>
                  </div>
                  <span>{{ scenario.effectiveness }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button @click="viewScenarioInsights(scenario.id)"
                    class="btn btn-sm btn-outline-info">
              <i class="fas fa-chart-line"></i> View Insights
            </button>
            <button @click="createExercise(scenario.id)"
                    class="btn btn-sm btn-success">
              <i class="fas fa-play"></i> Create Exercise
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Recommendations Panel -->
    <div class="ai-recommendations-section mt-5">
      <div class="section-header">
        <h4><i class="fas fa-lightbulb"></i> AI Improvement Recommendations</h4>
      </div>

      <div class="recommendations-list">
        <div v-for="recommendation in improvementRecommendations"
             :key="recommendation.id"
             class="recommendation-card">
          <div class="recommendation-header">
            <div class="rec-type">
              <i :class="getRecommendationIcon(recommendation.type)"></i>
              <span>{{ recommendation.type }}</span>
            </div>
            <div class="rec-priority" :class="getPriorityClass(recommendation.priority)">
              {{ recommendation.priority }}
            </div>
          </div>
          <div class="recommendation-body">
            <h6>{{ recommendation.title }}</h6>
            <p>{{ recommendation.description }}</p>
            <div class="rec-details">
              <span class="confidence">
                <i class="fas fa-percentage"></i>
                {{ recommendation.confidence }}% Confidence
              </span>
              <span class="impact">
                <i class="fas fa-arrow-up"></i>
                {{ recommendation.expected_impact }}% Expected Improvement
              </span>
            </div>
          </div>
          <div class="recommendation-actions">
            <button @click="implementRecommendation(recommendation.id)"
                    class="btn btn-sm btn-success">
              <i class="fas fa-check"></i> Implement
            </button>
            <button @click="viewRecommendationDetails(recommendation.id)"
                    class="btn btn-sm btn-outline-info">
              <i class="fas fa-info-circle"></i> Details
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Line, Doughnut, Bar } from 'vue-chartjs';

export default {
  name: 'LearningAnalyticsDashboard',
  components: {
    Line,
    Doughnut,
    Bar
  },
  data() {
    return {
      learningData: {},
      topScenarios: [],
      improvementRecommendations: [],
      isRefreshing: false,
      lastUpdated: null,

      // Chart data
      effectivenessTrendData: {},
      scenarioPerformanceData: {},
      exerciseTypeData: {},
      aiVsManualData: {},

      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    }
  },

  async mounted() {
    await this.loadAnalytics();
    this.setupRealTimeUpdates();
  },

  methods: {
    async loadAnalytics() {
      try {
        // Load learning data from Scenario Orchestrator
        const response = await this.$http.get('http://localhost:8085/learning/dashboard');
        this.learningData = response.data.dashboard || {};

        // Load top scenarios
        this.topScenarios = this.learningData.top_performing_scenarios || [];

        // Load improvement recommendations
        await this.loadImprovementRecommendations();

        // Update charts
        this.updateChartData();

        this.lastUpdated = new Date().toLocaleString();

      } catch (error) {
        this.$toast.error('Failed to load learning analytics: ' + error.message);
      }
    },

    async refreshAnalytics() {
      this.isRefreshing = true;
      await this.loadAnalytics();
      this.isRefreshing = false;
      this.$toast.success('Analytics refreshed successfully');
    },

    setupRealTimeUpdates() {
      // WebSocket for real-time learning updates
      if (this.ws) {
        this.ws.close();
      }

      this.ws = new WebSocket('ws://localhost:8085/ws/learning-updates');

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'learning_update') {
          // Update specific scenario data
          this.updateScenarioLearning(data.scenario_id, data.learning_data);
        } else if (data.type === 'new_recommendation') {
          // Add new AI recommendation
          this.improvementRecommendations.unshift(data.recommendation);
        }
      };
    }
  }
}
</script>
```

---

## 📋 **Technical Requirements для Interface Team**

### **API Endpoints для ЭТАП 5:**

```javascript
// Analytics API (bcm_reporting)
GET  /api/analytics/dashboard/{dashboard_type}    # Get analytics data
POST /api/analytics/dashboard/refresh            # Refresh analytics
GET  /api/analytics/scenario-effectiveness       # Scenario effectiveness data

// Learning API (Scenario Orchestrator)
GET  /learning/dashboard                         # Platform learning overview
GET  /learning/scenario/{id}/insights            # Scenario-specific insights
POST /learning/exercise-result                   # Submit exercise results

// Knowledge Base API (bcm_community)
GET  /api/knowledge/articles                     # Get knowledge articles
POST /api/knowledge/articles/{id}/bookmark       # Bookmark article
GET  /api/knowledge/search                       # Search knowledge base
POST /api/knowledge/generate-from-exercise       # Auto-generate article
```

### **Environment Variables:**
```env
# Analytics Integration
VUE_APP_ANALYTICS_URL=http://localhost:8069/api/analytics
VUE_APP_LEARNING_URL=http://localhost:8085/learning
VUE_APP_KNOWLEDGE_URL=http://localhost:8069/bcm/community

# Grafana Integration
VUE_APP_GRAFANA_URL=http://localhost:3003
VUE_APP_GRAFANA_DASHBOARD_ID=bcm-platform-overview
```

---

## 🎯 **Priority Tasks для Interface Team:**

### **ПРИОРИТЕТ 1**: Analytics Dashboard (Odoo)
- **Время**: 3-4 дня
- **Технологии**: Odoo XML views + JavaScript widgets
- **Функции**: Executive summary, exercise analytics, AI insights

### **ПРИОРИТЕТ 2**: Knowledge Base Portal (Website)
- **Время**: 2-3 дня
- **Технологии**: Odoo website templates + Bootstrap
- **Функции**: Article browsing, search, categorization

### **ПРИОРИТЕТ 3**: Learning Analytics (Vue.js)
- **Время**: 2-3 дня
- **Технологии**: Vue 3 + Chart.js + WebSocket
- **Функции**: Real-time learning insights, trend analysis

---

## ✅ **ЭТАП 5: Complete Documentation + Interface Specs Ready!**

**Backend implementation + Analytics system + Knowledge base + Complete interface specifications готово!** 🧠📊📚

**Документация сохранена в:**
- `/docs/PHASE_5_MODULE_DOCUMENTATION.md`
- `/docs/frontend/PHASE_5_INTERFACE_SPECIFICATIONS.md`
- `/docs/PHASE_5_IMPLEMENTATION_COMPLETE.md`

**Готов к передаче команде интерфейсов!** 🎨🚀