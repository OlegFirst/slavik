-- =====================================================
-- PREDICTIVE SERVICE - DATABASE SCHEMA
-- =====================================================
--
-- Purpose: Store journey predictions, certification forecasts,
--          and track prediction accuracy
--
-- Features:
-- - Journey timeline predictions
-- - Certification date predictions
-- - Prediction accuracy tracking
-- - Demand forecasts for experts
--
-- =====================================================

-- =====================================================
-- 1. JOURNEY PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.journey_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Organization context
    org_id UUID NOT NULL,
    prediction_date TIMESTAMP NOT NULL DEFAULT NOW(),
    horizon_days INTEGER NOT NULL DEFAULT 90,

    -- Prediction data
    milestones JSONB NOT NULL DEFAULT '[]'::jsonb,
    timeline JSONB NOT NULL DEFAULT '[]'::jsonb,
    critical_path JSONB NOT NULL DEFAULT '[]'::jsonb,
    estimated_completion_date TIMESTAMP,
    confidence_overall DECIMAL(3,2) CHECK (confidence_overall >= 0 AND confidence_overall <= 1),

    -- Context for prediction
    current_module TEXT,
    current_stage TEXT,
    organization_data JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Similar orgs used
    similar_orgs_count INTEGER DEFAULT 0,
    similar_orgs_used JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),

    CONSTRAINT journey_predictions_org_fkey FOREIGN KEY (org_id)
        REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_journey_predictions_org
    ON public.journey_predictions(org_id);
CREATE INDEX IF NOT EXISTS idx_journey_predictions_date
    ON public.journey_predictions(prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_journey_predictions_module
    ON public.journey_predictions(current_module);

-- Comments
COMMENT ON TABLE public.journey_predictions IS 'AI-predicted journey timelines for organizations';
COMMENT ON COLUMN public.journey_predictions.milestones IS 'Array of predicted milestones with dates and confidence';
COMMENT ON COLUMN public.journey_predictions.timeline IS 'Full timeline of predicted events';
COMMENT ON COLUMN public.journey_predictions.confidence_overall IS 'Overall prediction confidence (0-1)';

-- =====================================================
-- 2. CERTIFICATION PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS public.certification_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Organization
    org_id UUID NOT NULL,
    prediction_date TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Prediction
    predicted_certification_date TIMESTAMP NOT NULL,
    months_remaining DECIMAL(4,1),
    success_probability DECIMAL(3,2) CHECK (success_probability >= 0 AND success_probability <= 1),
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),

    -- Basis
    based_on_orgs_count INTEGER DEFAULT 0,
    similar_orgs JSONB DEFAULT '[]'::jsonb,
    key_factors JSONB DEFAULT '[]'::jsonb,

    -- Actual outcome (filled when certification happens)
    actual_certification_date TIMESTAMP,
    actual_success BOOLEAN,
    accuracy_error_days INTEGER,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT certification_predictions_org_fkey FOREIGN KEY (org_id)
        REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cert_predictions_org
    ON public.certification_predictions(org_id);
CREATE INDEX IF NOT EXISTS idx_cert_predictions_date
    ON public.certification_predictions(prediction_date DESC);

-- Comments
COMMENT ON TABLE public.certification_predictions IS 'Predictions for ISO 22301 certification timeline';
COMMENT ON COLUMN public.certification_predictions.success_probability IS 'Probability of successful certification (0-1)';
COMMENT ON COLUMN public.certification_predictions.actual_certification_date IS 'Actual date when certified (for accuracy tracking)';

-- =====================================================
-- 3. PREDICTION ACCURACY TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS public.prediction_accuracy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to prediction
    prediction_id UUID NOT NULL,
    prediction_type TEXT NOT NULL CHECK (prediction_type IN ('journey', 'certification', 'milestone', 'demand')),

    -- Predicted vs Actual
    milestone TEXT,
    predicted_date TIMESTAMP NOT NULL,
    actual_date TIMESTAMP NOT NULL,
    error_days INTEGER NOT NULL,
    error_percentage DECIMAL(5,2),

    -- Confidence
    predicted_confidence DECIMAL(3,2),
    confidence_vs_accuracy DECIMAL(4,2),  -- How well confidence matched accuracy

    -- Context
    org_id UUID NOT NULL,
    module TEXT,

    -- Metadata
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT prediction_accuracy_org_fkey FOREIGN KEY (org_id)
        REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_prediction_accuracy_type
    ON public.prediction_accuracy(prediction_type);
CREATE INDEX IF NOT EXISTS idx_prediction_accuracy_module
    ON public.prediction_accuracy(module);
CREATE INDEX IF NOT EXISTS idx_prediction_accuracy_org
    ON public.prediction_accuracy(org_id);

-- Comments
COMMENT ON TABLE public.prediction_accuracy IS 'Track prediction accuracy to improve ML models';
COMMENT ON COLUMN public.prediction_accuracy.error_days IS 'Days between predicted and actual date';
COMMENT ON COLUMN public.prediction_accuracy.confidence_vs_accuracy IS 'Calibration metric: did high confidence mean accurate?';

-- =====================================================
-- 4. EXPERT DEMAND FORECASTS
-- =====================================================

CREATE TABLE IF NOT EXISTS public.expert_demand_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Forecast period
    forecast_date TIMESTAMP NOT NULL DEFAULT NOW(),
    horizon_days INTEGER NOT NULL DEFAULT 30,

    -- Demand by specialty
    specialty TEXT,
    region TEXT,
    expected_projects INTEGER NOT NULL DEFAULT 0,
    peak_week TEXT,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),

    -- Geographic distribution
    by_industry JSONB DEFAULT '{}'::jsonb,
    by_region JSONB DEFAULT '{}'::jsonb,
    by_specialty JSONB DEFAULT '{}'::jsonb,

    -- Actual demand (filled when period ends)
    actual_projects INTEGER,
    forecast_accuracy DECIMAL(5,2),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_demand_forecasts_date
    ON public.expert_demand_forecasts(forecast_date DESC);
CREATE INDEX IF NOT EXISTS idx_demand_forecasts_specialty
    ON public.expert_demand_forecasts(specialty);
CREATE INDEX IF NOT EXISTS idx_demand_forecasts_region
    ON public.expert_demand_forecasts(region);

-- Comments
COMMENT ON TABLE public.expert_demand_forecasts IS 'Forecast demand for BCM consultants and auditors';
COMMENT ON COLUMN public.expert_demand_forecasts.specialty IS 'BIA, risk, planning, audit, etc.';

-- =====================================================
-- 5. PROACTIVE RECOMMENDATIONS LOG
-- =====================================================

CREATE TABLE IF NOT EXISTS public.proactive_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Target
    org_id UUID NOT NULL,
    user_id UUID REFERENCES auth.users(id),

    -- Recommendation
    type TEXT NOT NULL CHECK (type IN ('milestone_approaching', 'expert_needed', 'challenge_predicted', 'resource_required')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    milestone TEXT,
    days_until INTEGER,
    confidence DECIMAL(3,2),

    -- Content
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    actions JSONB DEFAULT '[]'::jsonb,
    resources JSONB DEFAULT '[]'::jsonb,

    -- Delivery
    sent_at TIMESTAMP,
    sent_via TEXT[],  -- ['email', 'push', 'in_app']
    notification_ids JSONB DEFAULT '[]'::jsonb,

    -- User action
    viewed_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    action_taken TEXT,
    action_taken_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT proactive_recommendations_org_fkey FOREIGN KEY (org_id)
        REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_proactive_recommendations_org
    ON public.proactive_recommendations(org_id);
CREATE INDEX IF NOT EXISTS idx_proactive_recommendations_user
    ON public.proactive_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_proactive_recommendations_type
    ON public.proactive_recommendations(type);
CREATE INDEX IF NOT EXISTS idx_proactive_recommendations_sent
    ON public.proactive_recommendations(sent_at DESC) WHERE sent_at IS NOT NULL;

-- Comments
COMMENT ON TABLE public.proactive_recommendations IS 'Log of AI-generated proactive recommendations sent to users';
COMMENT ON COLUMN public.proactive_recommendations.type IS 'Type of recommendation triggered';
COMMENT ON COLUMN public.proactive_recommendations.action_taken IS 'What action user took in response';

-- =====================================================
-- 6. ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS
ALTER TABLE public.journey_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.certification_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prediction_accuracy ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expert_demand_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.proactive_recommendations ENABLE ROW LEVEL SECURITY;

-- Journey Predictions Policies
CREATE POLICY "Users can view predictions for their organization"
    ON public.journey_predictions
    FOR SELECT
    USING (
        org_id IN (
            SELECT organization_id
            FROM public.organization_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage journey predictions"
    ON public.journey_predictions
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Certification Predictions Policies
CREATE POLICY "Users can view cert predictions for their organization"
    ON public.certification_predictions
    FOR SELECT
    USING (
        org_id IN (
            SELECT organization_id
            FROM public.organization_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage cert predictions"
    ON public.certification_predictions
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Prediction Accuracy Policies
CREATE POLICY "Service role can manage prediction accuracy"
    ON public.prediction_accuracy
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Expert Demand Forecasts Policies (public for experts)
CREATE POLICY "Authenticated users can view demand forecasts"
    ON public.expert_demand_forecasts
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can manage demand forecasts"
    ON public.expert_demand_forecasts
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Proactive Recommendations Policies
CREATE POLICY "Users can view their own recommendations"
    ON public.proactive_recommendations
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own recommendations (view/dismiss)"
    ON public.proactive_recommendations
    FOR UPDATE
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Service role can manage recommendations"
    ON public.proactive_recommendations
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Calculate prediction accuracy stats
CREATE OR REPLACE FUNCTION public.get_prediction_accuracy_stats(
    p_prediction_type TEXT DEFAULT NULL,
    p_module TEXT DEFAULT NULL,
    p_days INTEGER DEFAULT 90
)
RETURNS TABLE (
    prediction_type TEXT,
    module TEXT,
    total_predictions BIGINT,
    avg_error_days NUMERIC,
    median_error_days NUMERIC,
    accuracy_within_7_days NUMERIC,
    accuracy_within_14_days NUMERIC,
    confidence_calibration NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pa.prediction_type,
        pa.module,
        COUNT(*)::BIGINT as total_predictions,
        ROUND(AVG(ABS(pa.error_days)), 1) as avg_error_days,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(pa.error_days)) as median_error_days,
        ROUND(COUNT(*) FILTER (WHERE ABS(pa.error_days) <= 7) * 100.0 / COUNT(*), 1) as accuracy_within_7_days,
        ROUND(COUNT(*) FILTER (WHERE ABS(pa.error_days) <= 14) * 100.0 / COUNT(*), 1) as accuracy_within_14_days,
        ROUND(AVG(pa.confidence_vs_accuracy), 2) as confidence_calibration
    FROM public.prediction_accuracy pa
    WHERE
        (p_prediction_type IS NULL OR pa.prediction_type = p_prediction_type)
        AND (p_module IS NULL OR pa.module = p_module)
        AND pa.recorded_at >= NOW() - INTERVAL '1 day' * p_days
    GROUP BY pa.prediction_type, pa.module;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get latest prediction for organization
CREATE OR REPLACE FUNCTION public.get_latest_journey_prediction(p_org_id UUID)
RETURNS SETOF public.journey_predictions AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM public.journey_predictions
    WHERE org_id = p_org_id
    ORDER BY prediction_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get active recommendations for organization
CREATE OR REPLACE FUNCTION public.get_active_recommendations(
    p_org_id UUID,
    p_user_id UUID DEFAULT NULL
)
RETURNS SETOF public.proactive_recommendations AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM public.proactive_recommendations
    WHERE
        org_id = p_org_id
        AND (p_user_id IS NULL OR user_id = p_user_id)
        AND dismissed_at IS NULL
        AND created_at >= NOW() - INTERVAL '30 days'
    ORDER BY priority DESC, created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 8. TRIGGERS
-- =====================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_journey_predictions_updated_at
    BEFORE UPDATE ON public.journey_predictions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_certification_predictions_updated_at
    BEFORE UPDATE ON public.certification_predictions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- 9. GRANT PERMISSIONS
-- =====================================================

-- Grant service role full access
GRANT ALL ON public.journey_predictions TO service_role;
GRANT ALL ON public.certification_predictions TO service_role;
GRANT ALL ON public.prediction_accuracy TO service_role;
GRANT ALL ON public.expert_demand_forecasts TO service_role;
GRANT ALL ON public.proactive_recommendations TO service_role;

-- Grant authenticated users read access (controlled by RLS)
GRANT SELECT ON public.journey_predictions TO authenticated;
GRANT SELECT ON public.certification_predictions TO authenticated;
GRANT SELECT ON public.expert_demand_forecasts TO authenticated;
GRANT SELECT, UPDATE ON public.proactive_recommendations TO authenticated;

-- =====================================================
-- END OF MIGRATION
-- =====================================================

-- Verification
DO $$
BEGIN
    RAISE NOTICE '✅ Predictive Service schema created successfully';
    RAISE NOTICE '   - journey_predictions table';
    RAISE NOTICE '   - certification_predictions table';
    RAISE NOTICE '   - prediction_accuracy table';
    RAISE NOTICE '   - expert_demand_forecasts table';
    RAISE NOTICE '   - proactive_recommendations table';
    RAISE NOTICE '   - RLS policies enabled';
    RAISE NOTICE '   - Helper functions created';
END $$;
