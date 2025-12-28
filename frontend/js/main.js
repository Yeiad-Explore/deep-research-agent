/**
 * Main Application Logic
 * Coordinates API calls and UI updates
 */

// Initialize API client
const api = new ResearchAPI();

// Store current research data
let currentResearchData = null;

// DOM Elements
const startButton = document.getElementById('start-research');
const queryInput = document.getElementById('query');
const depthSelect = document.getElementById('depth');
const includeRedditCheckbox = document.getElementById('include-reddit');
const subredditsInput = document.getElementById('subreddits');
const timeFilterSelect = document.getElementById('time-filter');
const toggleOptionsButton = document.getElementById('toggle-options');
const optionsContent = document.getElementById('options-content');
const progressTracker = document.getElementById('progress-tracker');
const discoveriesFeed = document.getElementById('discoveries-feed');
const resultsContainer = document.getElementById('results-container');
const exportMarkdownButton = document.getElementById('export-markdown');
const exportJsonButton = document.getElementById('export-json');
const refineButton = document.getElementById('refine-research');

// Tab elements
const tabs = document.querySelectorAll('.tab');
const tabContent = document.getElementById('tab-content');

/**
 * Initialize application
 */
function init() {
    console.log('Initializing Deep Research Agent...');

    // Toggle advanced options
    toggleOptionsButton.addEventListener('click', () => {
        const isVisible = optionsContent.style.display !== 'none';
        optionsContent.style.display = isVisible ? 'none' : 'block';
        toggleOptionsButton.textContent = isVisible ? '⚙️ Advanced Options' : '⚙️ Hide Options';
    });

    // Start research button
    startButton.addEventListener('click', startResearch);

    // Allow Enter key to start research
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startResearch();
        }
    });

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    // Export buttons
    exportMarkdownButton.addEventListener('click', exportAsMarkdown);
    exportJsonButton.addEventListener('click', exportAsJson);

    // Refine research button
    refineButton.addEventListener('click', refineResearch);

    // Listen for research updates
    window.addEventListener('research-update', handleResearchUpdate);

    console.log('Initialization complete');
}

/**
 * Start research process
 */
async function startResearch() {
    const query = queryInput.value.trim();

    if (!query) {
        alert('Please enter a research question');
        return;
    }

    // Disable button
    startButton.disabled = true;
    startButton.textContent = 'Researching...';

    // Reset UI
    UI.reset();

    // Show progress sections
    progressTracker.style.display = 'block';
    discoveriesFeed.style.display = 'block';

    // Gather config
    const config = {
        depth: depthSelect.value,
        max_iterations: depthSelect.value === 'quick' ? 1 : depthSelect.value === 'standard' ? 3 : 5,
        include_reddit: includeRedditCheckbox.checked,
        subreddits: subredditsInput.value ? subredditsInput.value.split(',').map(s => s.trim()) : null,
        time_filter: timeFilterSelect.value,
        max_web_results: 15,
        max_reddit_posts: 50
    };

    console.log('Starting research:', query, config);

    try {
        // Start research with WebSocket streaming
        const result = await api.startResearchStream(query, config);
        console.log('Research complete:', result);

        currentResearchData = result;

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Research error:', error);
        UI.showError(error.message || 'An error occurred during research');
    } finally {
        // Re-enable button
        startButton.disabled = false;
        startButton.textContent = '🚀 Start Deep Research';
    }
}

/**
 * Handle research update events
 */
function handleResearchUpdate(event) {
    const data = event.detail;
    console.log('Research update:', data);

    if (data.status === 'started') {
        UI.addDiscovery('System', `Research started: ${data.query}`);
    } else if (data.status === 'in_progress') {
        // Update stage
        UI.updateStage(data.stage, 'in_progress', data.message);

        // Add discovery
        if (data.message) {
            UI.addDiscovery('Progress', data.message);
        }

        // Add specific discoveries
        if (data.data) {
            if (data.data.web_results > 0) {
                UI.addDiscovery('Web', `Found ${data.data.web_results} web results`);
            }
            if (data.data.reddit_posts > 0) {
                UI.addDiscovery('Reddit', `Found ${data.data.reddit_posts} Reddit posts`);
            }
        }

        // Mark previous stages as completed
        markPreviousStagesComplete(data.stage);
    } else if (data.status === 'complete') {
        UI.addDiscovery('System', 'Research completed successfully!');

        // Mark all stages as completed
        const stages = ['planning', 'searching', 'scraping', 'analyzing', 'consensus', 'synthesis'];
        stages.forEach(stage => UI.updateStage(stage, 'completed'));
    } else if (data.status === 'error') {
        UI.addDiscovery('Error', data.message);
    }
}

/**
 * Mark previous stages as complete
 */
function markPreviousStagesComplete(currentStage) {
    const stageOrder = ['query_planner', 'multi_source_searcher', 'content_scraper', 'content_analyzer', 'consensus_builder', 'synthesis'];
    const currentIndex = stageOrder.indexOf(currentStage);

    if (currentIndex > 0) {
        for (let i = 0; i < currentIndex; i++) {
            UI.updateStage(stageOrder[i], 'completed');
        }
    }
}

/**
 * Display research results
 */
function displayResults(data) {
    currentResearchData = data;

    // Show results container
    resultsContainer.style.display = 'block';

    // Render executive summary
    const executiveSummary = document.getElementById('executive-summary');
    executiveSummary.innerHTML = `
        <h3>📋 Executive Summary</h3>
        <p><strong>Research Question:</strong> ${queryInput.value}</p>
        <p><strong>Total Sources:</strong> ${(data.web_summaries?.length || 0) + (data.reddit_summaries?.length || 0)}</p>
        <p><strong>Web Sources:</strong> ${data.web_summaries?.length || 0}</p>
        <p><strong>Reddit Sources:</strong> ${data.reddit_summaries?.length || 0}</p>
        <p><strong>Confidence Level:</strong> ${data.confidence_scores?.overall || 'medium'}</p>
    `;

    // Show default tab (synthesis)
    switchTab('synthesis');
}

/**
 * Switch tab
 */
function switchTab(tabName) {
    if (!currentResearchData) return;

    // Update active tab
    tabs.forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Render content based on tab
    let content = '';

    switch (tabName) {
        case 'synthesis':
            content = UI.renderSynthesis(
                currentResearchData.final_synthesis,
                currentResearchData.confidence_scores
            );
            break;

        case 'web-sources':
            content = UI.renderWebSources(currentResearchData.web_summaries);
            break;

        case 'reddit-insights':
            content = UI.renderRedditInsights(currentResearchData);
            break;

        case 'expert-opinions':
            content = UI.renderExpertOpinions(currentResearchData.expert_opinions);
            break;

        case 'consensus':
            content = UI.renderConsensus(
                currentResearchData.community_consensus,
                currentResearchData.cross_reference
            );
            break;

        case 'all-sources':
            content = UI.renderAllSources(currentResearchData.sources);
            break;

        default:
            content = '<p>No content available</p>';
    }

    tabContent.innerHTML = content;
}

/**
 * Export research as Markdown
 */
function exportAsMarkdown() {
    if (!currentResearchData) return;

    let markdown = `# Research Report\n\n`;
    markdown += `**Query:** ${queryInput.value}\n\n`;
    markdown += `**Date:** ${new Date().toLocaleDateString()}\n\n`;
    markdown += `---\n\n`;
    markdown += `## Executive Summary\n\n`;
    markdown += `- **Total Sources:** ${(currentResearchData.web_summaries?.length || 0) + (currentResearchData.reddit_summaries?.length || 0)}\n`;
    markdown += `- **Web Sources:** ${currentResearchData.web_summaries?.length || 0}\n`;
    markdown += `- **Reddit Sources:** ${currentResearchData.reddit_summaries?.length || 0}\n`;
    markdown += `- **Confidence:** ${currentResearchData.confidence_scores?.overall || 'medium'}\n\n`;
    markdown += `---\n\n`;
    markdown += `## Full Report\n\n`;
    markdown += currentResearchData.final_synthesis || 'No synthesis available';
    markdown += `\n\n---\n\n`;
    markdown += `## Sources\n\n`;

    (currentResearchData.sources || []).forEach((source, index) => {
        markdown += `${index + 1}. [${source.title}](${source.url})\n`;
    });

    // Download
    downloadFile(markdown, 'research-report.md', 'text/markdown');
}

/**
 * Export research as JSON
 */
function exportAsJson() {
    if (!currentResearchData) return;

    const json = JSON.stringify(currentResearchData, null, 2);
    downloadFile(json, 'research-data.json', 'application/json');
}

/**
 * Download file helper
 */
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

/**
 * Refine research
 */
async function refineResearch() {
    if (!api.currentSessionId) {
        alert('No active research session to refine');
        return;
    }

    const refinementQuery = prompt('What aspect would you like to focus on or add?');

    if (!refinementQuery) return;

    refineButton.disabled = true;
    refineButton.textContent = 'Refining...';

    try {
        const result = await api.refineResearch(api.currentSessionId, refinementQuery);
        console.log('Refinement complete:', result);

        currentResearchData = result;
        displayResults(result);

        UI.addDiscovery('System', 'Research refined successfully!');

    } catch (error) {
        console.error('Refinement error:', error);
        alert('Error refining research: ' + error.message);
    } finally {
        refineButton.disabled = false;
        refineButton.textContent = '🔄 Refine Research';
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
