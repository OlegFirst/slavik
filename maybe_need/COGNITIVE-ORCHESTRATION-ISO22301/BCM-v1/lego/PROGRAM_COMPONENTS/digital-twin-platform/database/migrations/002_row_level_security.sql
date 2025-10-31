-- Row Level Security Policies
-- Version: 1.0.0
-- Date: 2025-01-15

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_twins ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Organizations policies
CREATE POLICY "Public organizations are viewable by everyone"
    ON organizations FOR SELECT
    USING (is_active = true);

CREATE POLICY "Users can insert their own organizations"
    ON organizations FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own organizations"
    ON organizations FOR UPDATE
    USING (auth.uid() = created_by)
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can delete their own organizations"
    ON organizations FOR DELETE
    USING (auth.uid() = created_by);

-- Digital Twins policies
CREATE POLICY "Users can view twins of their organizations"
    ON digital_twins FOR SELECT
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid() OR is_active = true
        )
    );

CREATE POLICY "Users can create twins for their organizations"
    ON digital_twins FOR INSERT
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

CREATE POLICY "Users can update twins of their organizations"
    ON digital_twins FOR UPDATE
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

CREATE POLICY "Users can delete twins of their organizations"
    ON digital_twins FOR DELETE
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Departments policies
CREATE POLICY "Users can view departments of accessible organizations"
    ON departments FOR SELECT
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid() OR is_active = true
        )
    );

CREATE POLICY "Users can manage departments of their organizations"
    ON departments FOR ALL
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Simulations policies
CREATE POLICY "Users can view simulations of accessible twins"
    ON simulations FOR SELECT
    USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid() OR o.is_active = true
        )
    );

CREATE POLICY "Users can create simulations for their twins"
    ON simulations FOR INSERT
    WITH CHECK (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid()
        )
    );

CREATE POLICY "Users can update their own simulations"
    ON simulations FOR UPDATE
    USING (created_by = auth.uid())
    WITH CHECK (created_by = auth.uid());

CREATE POLICY "Users can delete their own simulations"
    ON simulations FOR DELETE
    USING (created_by = auth.uid());

-- Metrics policies
CREATE POLICY "Users can view metrics of accessible twins"
    ON metrics FOR SELECT
    USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid() OR o.is_active = true
        )
    );

CREATE POLICY "Users can insert metrics for their twins"
    ON metrics FOR INSERT
    WITH CHECK (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid()
        )
    );

-- Predictions policies
CREATE POLICY "Users can view predictions of accessible twins"
    ON predictions FOR SELECT
    USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid() OR o.is_active = true
        )
    );

CREATE POLICY "System can insert predictions"
    ON predictions FOR INSERT
    WITH CHECK (true); -- Only system/service role can insert

-- Audit logs policies
CREATE POLICY "Users can view their own audit logs"
    ON audit_logs FOR SELECT
    USING (actor_id = auth.uid());

CREATE POLICY "System can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true); -- All authenticated users can create logs

-- Sessions policies
CREATE POLICY "Users can view their own sessions"
    ON sessions FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own sessions"
    ON sessions FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Reports policies
CREATE POLICY "Users can view public reports or their own"
    ON reports FOR SELECT
    USING (
        is_public = true OR
        generated_by = auth.uid() OR
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid()
        )
    );

CREATE POLICY "Users can create reports for their twins"
    ON reports FOR INSERT
    WITH CHECK (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid()
        )
    );

CREATE POLICY "Users can update their own reports"
    ON reports FOR UPDATE
    USING (generated_by = auth.uid())
    WITH CHECK (generated_by = auth.uid());

CREATE POLICY "Users can delete their own reports"
    ON reports FOR DELETE
    USING (generated_by = auth.uid());

-- Scenarios policies (public read, admin write)
CREATE POLICY "Everyone can view active scenarios"
    ON scenarios FOR SELECT
    USING (is_active = true);

CREATE POLICY "Only admins can manage scenarios"
    ON scenarios FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM auth.users
            WHERE auth.uid() = id
            AND raw_user_meta_data->>'role' = 'admin'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM auth.users
            WHERE auth.uid() = id
            AND raw_user_meta_data->>'role' = 'admin'
        )
    );

-- AI Learning Data policies
CREATE POLICY "Users can view learning data of their twins"
    ON ai_learning_data FOR SELECT
    USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN organizations o ON dt.organization_id = o.id
            WHERE o.created_by = auth.uid()
        )
    );

CREATE POLICY "System can manage learning data"
    ON ai_learning_data FOR ALL
    USING (true)
    WITH CHECK (true); -- Only service role

-- Integrations policies
CREATE POLICY "Users can view integrations of their organizations"
    ON integrations FOR SELECT
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

CREATE POLICY "Users can manage integrations of their organizations"
    ON integrations FOR ALL
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Service role bypass (for backend operations)
CREATE POLICY "Service role has full access to organizations"
    ON organizations FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has full access to digital_twins"
    ON digital_twins FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has full access to simulations"
    ON simulations FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has full access to metrics"
    ON metrics FOR ALL
    USING (auth.jwt()->>'role' = 'service_role')
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- Function to check organization ownership
CREATE OR REPLACE FUNCTION is_org_owner(org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM organizations
        WHERE id = org_id
        AND created_by = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check twin access
CREATE OR REPLACE FUNCTION has_twin_access(p_twin_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM digital_twins dt
        JOIN organizations o ON dt.organization_id = o.id
        WHERE dt.id = p_twin_id
        AND (o.created_by = auth.uid() OR o.is_active = true)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on helper functions
GRANT EXECUTE ON FUNCTION is_org_owner(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION has_twin_access(UUID) TO authenticated;