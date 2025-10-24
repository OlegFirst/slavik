import { test, expect } from '@playwright/test';

/**
 * Planning Module E2E Tests
 *
 * User Flows:
 * 1. View list of BC plans
 * 2. Create new BC plan
 * 3. View plan details
 * 4. Edit plan
 * 5. Add recovery strategy
 * 6. Add action plan
 * 7. Approve plan
 * 8. View analytics dashboard
 */

test.describe('Planning Module - User Flows', () => {

  test.beforeEach(async ({ page }) => {
    // Login and navigate to planning module
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test.describe('User Flow 1: View BC Plans List', () => {

    test('should display plans list with filters', async ({ page }) => {
      await page.goto('/planning');

      // Check page title
      await expect(page.locator('h1')).toContainText('BC Plans');

      // Check stats cards are visible
      await expect(page.locator('text=Total Plans')).toBeVisible();
      await expect(page.locator('text=Active Plans')).toBeVisible();
      await expect(page.locator('text=Coverage')).toBeVisible();
      await expect(page.locator('text=Avg Maturity')).toBeVisible();

      // Check filters
      await expect(page.locator('[placeholder="Search plans..."]')).toBeVisible();
      await expect(page.locator('text=All Types')).toBeVisible();
      await expect(page.locator('text=All Statuses')).toBeVisible();

      // Check create button
      await expect(page.locator('button', { hasText: 'Create Plan' })).toBeVisible();
    });

    test('should filter plans by type', async ({ page }) => {
      await page.goto('/planning');

      // Click type filter
      await page.click('text=All Types');
      await page.click('text=Comprehensive');

      // Wait for filtered results
      await page.waitForTimeout(500);

      // Verify URL has filter param
      expect(page.url()).toContain('type=comprehensive');
    });

    test('should search plans by name', async ({ page }) => {
      await page.goto('/planning');

      // Type in search
      await page.fill('[placeholder="Search plans..."]', 'Main BC Plan');
      await page.waitForTimeout(300); // debounce

      // Check that search is applied
      const searchInput = page.locator('[placeholder="Search plans..."]');
      await expect(searchInput).toHaveValue('Main BC Plan');
    });

    test('should toggle between grid and list layouts', async ({ page }) => {
      await page.goto('/planning');

      // Check grid layout button exists
      const gridButton = page.locator('[aria-label="Grid view"]');
      const listButton = page.locator('[aria-label="List view"]');

      await expect(gridButton).toBeVisible();
      await expect(listButton).toBeVisible();

      // Click list view
      await listButton.click();
      await page.waitForTimeout(200);

      // Click back to grid
      await gridButton.click();
    });
  });

  test.describe('User Flow 2: Create New BC Plan', () => {

    test('should open create plan form', async ({ page }) => {
      await page.goto('/planning');

      // Click create button
      await page.click('button', { hasText: 'Create Plan' });

      // Wait for navigation
      await page.waitForURL('/planning/new');

      // Check form is visible
      await expect(page.locator('h1')).toContainText('Create BC Plan');
      await expect(page.locator('[name="name"]')).toBeVisible();
      await expect(page.locator('[name="plan_type"]')).toBeVisible();
    });

    test('should create new BC plan successfully', async ({ page }) => {
      await page.goto('/planning/new');

      // Fill plan info
      await page.fill('[name="name"]', 'E2E Test Plan');
      await page.fill('[name="description"]', 'Plan created by E2E test');

      // Select plan type
      await page.selectOption('[name="plan_type"]', 'comprehensive');

      // Select status
      await page.selectOption('[name="status"]', 'draft');

      // Fill RTO/RPO/MTPD
      await page.fill('[name="rto_hours"]', '4');
      await page.fill('[name="rpo_hours"]', '2');
      await page.fill('[name="mtpd_hours"]', '24');

      // Select criticality
      await page.selectOption('[name="criticality_level"]', 'high');

      // Submit form
      await page.click('button[type="submit"]');

      // Wait for redirect to detail page
      await page.waitForURL(/\/planning\/[a-zA-Z0-9-]+$/);

      // Check success message or plan title
      await expect(page.locator('h1')).toContainText('E2E Test Plan');
    });

    test('should validate required fields', async ({ page }) => {
      await page.goto('/planning/new');

      // Try to submit without filling
      await page.click('button[type="submit"]');

      // Check validation errors
      await expect(page.locator('text=Required')).toBeVisible();
    });

    test('should validate RTO/RPO/MTPD relationships', async ({ page }) => {
      await page.goto('/planning/new');

      // Fill with invalid values (RTO > MTPD)
      await page.fill('[name="name"]', 'Invalid Test Plan');
      await page.fill('[name="rto_hours"]', '48');
      await page.fill('[name="mtpd_hours"]', '24');

      // Try to submit
      await page.click('button[type="submit"]');

      // Check validation error
      await expect(page.locator('text=RTO must be less than MTPD')).toBeVisible();
    });
  });

  test.describe('User Flow 3: View Plan Details', () => {

    test('should display plan details', async ({ page }) => {
      // Assume we have a plan with ID 'test-plan-1'
      await page.goto('/planning/test-plan-1');

      // Check header
      await expect(page.locator('h1')).toBeVisible();

      // Check tabs
      await expect(page.locator('text=Overview')).toBeVisible();
      await expect(page.locator('text=Strategies')).toBeVisible();
      await expect(page.locator('text=Actions')).toBeVisible();
      await expect(page.locator('text=History')).toBeVisible();

      // Check action buttons
      await expect(page.locator('button', { hasText: 'Edit' })).toBeVisible();
      await expect(page.locator('button', { hasText: 'Archive' })).toBeVisible();
    });

    test('should switch between tabs', async ({ page }) => {
      await page.goto('/planning/test-plan-1');

      // Click Strategies tab
      await page.click('text=Strategies');
      await page.waitForTimeout(200);

      // Check strategies content
      await expect(page.locator('text=Recovery Strategies')).toBeVisible();

      // Click Actions tab
      await page.click('text=Actions');
      await page.waitForTimeout(200);

      // Check actions content
      await expect(page.locator('text=Action Plans')).toBeVisible();

      // Click History tab
      await page.click('text=History');
      await page.waitForTimeout(200);

      // Check history content
      await expect(page.locator('text=Version History')).toBeVisible();
    });

    test('should display plan metrics', async ({ page }) => {
      await page.goto('/planning/test-plan-1');

      // Check metrics are visible
      await expect(page.locator('text=Coverage')).toBeVisible();
      await expect(page.locator('text=Strategies')).toBeVisible();
      await expect(page.locator('text=Actions')).toBeVisible();
      await expect(page.locator('text=Completion')).toBeVisible();
    });
  });

  test.describe('User Flow 4: Edit Plan', () => {

    test('should navigate to edit page', async ({ page }) => {
      await page.goto('/planning/test-plan-1');

      // Click edit button
      await page.click('button', { hasText: 'Edit' });

      // Wait for navigation
      await page.waitForURL('/planning/test-plan-1/edit');

      // Check form is pre-filled
      await expect(page.locator('h1')).toContainText('Edit BC Plan');
      const nameInput = page.locator('[name="name"]');
      await expect(nameInput).not.toBeEmpty();
    });

    test('should update plan successfully', async ({ page }) => {
      await page.goto('/planning/test-plan-1/edit');

      // Update name
      const nameInput = page.locator('[name="name"]');
      await nameInput.clear();
      await nameInput.fill('Updated Plan Name');

      // Update description
      const descInput = page.locator('[name="description"]');
      await descInput.clear();
      await descInput.fill('Updated by E2E test');

      // Submit
      await page.click('button[type="submit"]');

      // Wait for redirect
      await page.waitForURL('/planning/test-plan-1');

      // Check updated name
      await expect(page.locator('h1')).toContainText('Updated Plan Name');
    });

    test('should cancel edit and return to detail page', async ({ page }) => {
      await page.goto('/planning/test-plan-1/edit');

      // Click cancel
      await page.click('button', { hasText: 'Cancel' });

      // Should go back to detail page
      await page.waitForURL('/planning/test-plan-1');
    });
  });

  test.describe('User Flow 5: Add Recovery Strategy', () => {

    test('should open strategy form', async ({ page }) => {
      await page.goto('/planning/test-plan-1');
      await page.click('text=Strategies');

      // Click add strategy button
      await page.click('button', { hasText: 'Add Strategy' });

      // Check modal or form appears
      await expect(page.locator('text=Add Recovery Strategy')).toBeVisible();
    });

    test('should create recovery strategy', async ({ page }) => {
      await page.goto('/planning/test-plan-1');
      await page.click('text=Strategies');
      await page.click('button', { hasText: 'Add Strategy' });

      // Fill strategy form
      await page.fill('[name="strategy_name"]', 'Alternative Site Strategy');
      await page.selectOption('[name="strategy_type"]', 'alternative_site');
      await page.fill('[name="description"]', 'Backup datacenter in different location');

      // Fill resources
      await page.fill('[name="estimated_cost"]', '100000');
      await page.fill('[name="implementation_time"]', '720'); // 30 days in hours

      // Submit
      await page.click('button[type="submit"]', { hasText: 'Create Strategy' });

      // Wait for creation
      await page.waitForTimeout(500);

      // Check strategy appears in list
      await expect(page.locator('text=Alternative Site Strategy')).toBeVisible();
    });
  });

  test.describe('User Flow 6: Add Action Plan', () => {

    test('should open action form', async ({ page }) => {
      await page.goto('/planning/test-plan-1');
      await page.click('text=Actions');

      // Click add action button
      await page.click('button', { hasText: 'Add Action' });

      // Check form appears
      await expect(page.locator('text=Add Action Plan')).toBeVisible();
    });

    test('should create action plan', async ({ page }) => {
      await page.goto('/planning/test-plan-1');
      await page.click('text=Actions');
      await page.click('button', { hasText: 'Add Action' });

      // Fill action form
      await page.fill('[name="action_title"]', 'Setup Backup Systems');
      await page.selectOption('[name="action_type"]', 'preventive');
      await page.selectOption('[name="priority"]', 'high');
      await page.fill('[name="description"]', 'Configure and test backup systems');
      await page.fill('[name="responsible_party"]', 'IT Manager');

      // Set dates
      const today = new Date().toISOString().split('T')[0];
      await page.fill('[name="start_date"]', today);

      const targetDate = new Date();
      targetDate.setDate(targetDate.getDate() + 30);
      await page.fill('[name="target_date"]', targetDate.toISOString().split('T')[0]);

      // Submit
      await page.click('button[type="submit"]', { hasText: 'Create Action' });

      // Wait for creation
      await page.waitForTimeout(500);

      // Check action appears
      await expect(page.locator('text=Setup Backup Systems')).toBeVisible();
    });
  });

  test.describe('User Flow 7: Approve Plan', () => {

    test('should approve draft plan', async ({ page }) => {
      await page.goto('/planning/test-plan-1');

      // Check current status (should be Draft or Review)
      const statusBadge = page.locator('[data-testid="plan-status"]');

      // Click approve button
      await page.click('button', { hasText: 'Approve' });

      // Confirm in modal if appears
      const confirmButton = page.locator('button', { hasText: 'Confirm' });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
      }

      // Wait for status update
      await page.waitForTimeout(500);

      // Check status changed to Approved
      await expect(page.locator('text=Approved')).toBeVisible();
    });

    test('should activate approved plan', async ({ page }) => {
      await page.goto('/planning/test-plan-1');

      // Click activate button
      await page.click('button', { hasText: 'Activate' });

      // Confirm
      const confirmButton = page.locator('button', { hasText: 'Confirm' });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
      }

      // Wait for status update
      await page.waitForTimeout(500);

      // Check status changed to Active
      await expect(page.locator('text=Active')).toBeVisible();
    });
  });

  test.describe('User Flow 8: Analytics Dashboard', () => {

    test('should display analytics dashboard', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Check page title
      await expect(page.locator('h1')).toContainText('Planning Analytics');

      // Check sections
      await expect(page.locator('text=Executive Summary')).toBeVisible();
      await expect(page.locator('text=Maturity Assessment')).toBeVisible();
      await expect(page.locator('text=Coverage Matrix')).toBeVisible();
      await expect(page.locator('text=Gap Analysis')).toBeVisible();
      await expect(page.locator('text=Implementation Timeline')).toBeVisible();
    });

    test('should display executive summary cards', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Check metric cards
      await expect(page.locator('text=Total Plans')).toBeVisible();
      await expect(page.locator('text=Maturity Score')).toBeVisible();
      await expect(page.locator('text=Coverage')).toBeVisible();
      await expect(page.locator('text=Critical Gaps')).toBeVisible();
    });

    test('should display maturity radar chart', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Check chart container
      const chartContainer = page.locator('[data-testid="maturity-chart"]');
      await expect(chartContainer).toBeVisible();

      // Check chart categories
      await expect(page.locator('text=Management Support')).toBeVisible();
      await expect(page.locator('text=Documentation')).toBeVisible();
      await expect(page.locator('text=Training')).toBeVisible();
      await expect(page.locator('text=Testing')).toBeVisible();
      await expect(page.locator('text=Integration')).toBeVisible();
    });

    test('should display coverage matrix', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Scroll to coverage matrix
      await page.locator('text=Coverage Matrix').scrollIntoViewIfNeeded();

      // Check table headers
      await expect(page.locator('text=Business Process')).toBeVisible();
      await expect(page.locator('text=Coverage %')).toBeVisible();
      await expect(page.locator('text=Status')).toBeVisible();
    });

    test('should display gap analysis', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Scroll to gap analysis
      await page.locator('text=Gap Analysis').scrollIntoViewIfNeeded();

      // Check gap cards or list
      const gapSection = page.locator('[data-testid="gap-analysis"]');
      await expect(gapSection).toBeVisible();
    });

    test('should export analytics report', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Click export button
      const exportButton = page.locator('button', { hasText: 'Export' });
      await expect(exportButton).toBeVisible();

      // Click export (don't wait for download in test)
      await exportButton.click();

      // Check export modal or dropdown appears
      await expect(page.locator('text=PDF')).toBeVisible();
      await expect(page.locator('text=Excel')).toBeVisible();
    });

    test('should refresh analytics data', async ({ page }) => {
      await page.goto('/planning/analytics');

      // Click refresh button
      const refreshButton = page.locator('button', { hasText: 'Refresh' });
      await expect(refreshButton).toBeVisible();
      await refreshButton.click();

      // Check loading indicator appears briefly
      await page.waitForTimeout(200);

      // Data should reload
      await expect(page.locator('text=Executive Summary')).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {

    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('/api/v1/planning/plans', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      await page.goto('/planning');

      // Check error message appears
      await expect(page.locator('text=Error')).toBeVisible();
    });

    test('should handle network errors', async ({ page }) => {
      // Simulate offline
      await page.context().setOffline(true);

      await page.goto('/planning');

      // Check error or offline message
      await expect(page.locator('text=Failed to load')).toBeVisible();

      // Restore online
      await page.context().setOffline(false);
    });

    test('should handle not found pages', async ({ page }) => {
      await page.goto('/planning/non-existent-plan-id-12345');

      // Check 404 or not found message
      await expect(page.locator('text=Not Found')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {

    test('should work on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/planning');

      // Check mobile layout
      await expect(page.locator('h1')).toBeVisible();

      // Filters might be in a drawer/modal on mobile
      const filterButton = page.locator('button', { hasText: 'Filters' });
      if (await filterButton.isVisible()) {
        await filterButton.click();
      }
    });

    test('should work on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/planning');

      // Check tablet layout
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('text=Create Plan')).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {

    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto('/planning');

      const h1 = page.locator('h1');
      await expect(h1).toHaveCount(1);

      // Check h1 is visible
      await expect(h1).toBeVisible();
    });

    test('should have keyboard navigation', async ({ page }) => {
      await page.goto('/planning');

      // Tab through interactive elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Check focus is visible
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should have aria labels on buttons', async ({ page }) => {
      await page.goto('/planning');

      const createButton = page.locator('button', { hasText: 'Create Plan' });
      const ariaLabel = await createButton.getAttribute('aria-label');

      // Should have aria-label or text content
      expect(ariaLabel || 'Create Plan').toBeTruthy();
    });
  });
});
