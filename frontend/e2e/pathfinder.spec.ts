import { test, expect } from '@playwright/test';

test.describe('AI Pathfinder E2E', () => {
  
  test('should load the conversational goal intake form', async ({ page }) => {
    // Note: This assumes the app is running on localhost:3000 and page.tsx includes GoalChat
    // For this test to pass, page.tsx needs to be implemented.
    await page.goto('/');
    
    // Check for the title
    await expect(page.locator('text=AI Learning Pathfinder')).toBeVisible();
    
    // Check for the input field
    const input = page.locator('input[placeholder*="E.g., I want to become a DevOps engineer"]');
    await expect(input).toBeVisible();
    
    // Check for the submit button
    const button = page.locator('button[type="submit"]');
    await expect(button).toBeVisible();
  });

  test('should display loading state when submitting a goal', async ({ page }) => {
    await page.goto('/');
    
    // Intercept the API call to delay it, allowing us to see the loading state
    await page.route('**/api/generate-roadmap', async route => {
      // Delay for 1 second
      await new Promise(f => setTimeout(f, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          profile: { target_role: 'Test Role', skills: {}, weekly_hours: 10, learning_pace: 'medium' },
          roadmap: { 
            roadmap_id: 'test-123', 
            title: 'Test Roadmap', 
            target_role: 'Test Role', 
            total_estimated_weeks: 10, 
            total_hours: 100, 
            learner_summary: 'Test summary', 
            skill_gap_summary: ['Skill A'], 
            nodes: [], 
            edges: [] 
          }
        })
      });
    });

    // Type a goal and submit
    const input = page.locator('input[placeholder*="E.g., I want to become a DevOps engineer"]');
    await input.fill('I want to learn Playwright testing');
    
    const button = page.locator('button[type="submit"]');
    await button.click();

    // Verify loading spinner overlay is visible
    await expect(page.locator('text=Synthesizing your personalized roadmap...')).toBeVisible();
  });

});
