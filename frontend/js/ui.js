/**
 * UI Rendering and Management
 * Handles all UI updates and rendering
 */

const UI = {
    /**
     * Update progress stage
     */
    updateStage(stageName, status, message = '') {
        const stageMap = {
            'query_planner': 'planning',
            'multi_source_searcher': 'searching',
            'content_scraper': 'scraping',
            'content_analyzer': 'analyzing',
            'consensus_builder': 'consensus',
            'cross_reference': 'analyzing',
            'synthesis': 'synthesis',
            'quality_checker': 'synthesis',
            'gap_filler': 'searching'
        };

        const mappedStage = stageMap[stageName] || stageName;
        const stageElement = document.getElementById(`stage-${mappedStage}`);

        if (stageElement) {
            const statusElement = stageElement.querySelector('.status');
            statusElement.textContent = status;
            statusElement.className = `status ${status}`;

            if (status === 'in_progress') {
                stageElement.classList.add('active');
            } else {
                stageElement.classList.remove('active');
            }
        }
    },

    /**
     * Add live discovery to feed
     */
    addDiscovery(type, content) {
        const feed = document.getElementById('live-updates');
        const discovery = document.createElement('div');
        discovery.className = `discovery discovery-${type}`;

        const time = new Date().toLocaleTimeString();

        discovery.innerHTML = `
            <span class="discovery-type">${type}</span>
            <span class="discovery-content">${content}</span>
            <span class="discovery-time">${time}</span>
        `;

        feed.insertBefore(discovery, feed.firstChild);

        // Limit discoveries to 20
        while (feed.children.length > 20) {
            feed.removeChild(feed.lastChild);
        }
    },

    /**
     * Render full synthesis report
     */
    renderSynthesis(synthesis, confidenceScores) {
        return `
            <div class="content-section">
                <div class="synthesis-content">
                    ${this.formatMarkdown(synthesis)}
                </div>
                ${confidenceScores ? `
                    <div class="confidence-section">
                        <h4>Research Confidence</h4>
                        <p><strong>Overall Confidence:</strong> ${confidenceScores.overall || 'medium'}</p>
                        <p><strong>Web Sources:</strong> ${confidenceScores.web_sources || 0}</p>
                        <p><strong>Reddit Sources:</strong> ${confidenceScores.reddit_sources || 0}</p>
                        <p><strong>Corroborated Facts:</strong> ${confidenceScores.corroboration || 0}</p>
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render web sources
     */
    renderWebSources(summaries) {
        if (!summaries || summaries.length === 0) {
            return '<p>No web sources found.</p>';
        }

        return `
            <div class="content-section">
                <h4>Web Sources (${summaries.length})</h4>
                ${summaries.map((source, index) => `
                    <div class="source-item">
                        <h5>${index + 1}. ${source.title || 'Untitled'}</h5>
                        <p>${source.summary || 'No summary available'}</p>
                        <div class="source-meta">
                            <span>🔗 <a href="${source.url}" target="_blank">${source.url}</a></span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Render Reddit insights
     */
    renderRedditInsights(data) {
        const summaries = data.reddit_summaries || [];
        const consensus = data.community_consensus || {};

        if (summaries.length === 0) {
            return '<p>No Reddit discussions found.</p>';
        }

        const sentimentEmoji = {
            'positive': '😊',
            'negative': '😟',
            'neutral': '😐',
            'mixed': '🤔'
        };

        return `
            <div class="content-section">
                <h4>Community Consensus</h4>
                <div class="consensus-analysis">
                    <p><strong>Overall Sentiment:</strong> ${sentimentEmoji[consensus.sentiment] || ''} ${consensus.sentiment || 'neutral'}</p>
                    <p><strong>Agreement Level:</strong> ${consensus.agreement_level || 'unknown'}</p>
                    ${consensus.themes && consensus.themes.length > 0 ? `
                        <p><strong>Key Themes:</strong> ${consensus.themes.join(', ')}</p>
                    ` : ''}
                    ${consensus.majority_opinion ? `
                        <p><strong>Majority Opinion:</strong> ${consensus.majority_opinion}</p>
                    ` : ''}
                </div>

                <h4>Top Reddit Discussions (${summaries.length})</h4>
                ${summaries.map((thread, index) => `
                    <div class="reddit-thread">
                        <h5>${index + 1}. ${thread.title || 'Untitled'}</h5>
                        <div class="thread-meta">
                            <span>💬 ${thread.num_comments || 0} comments</span>
                        </div>
                        <p>${thread.summary || 'No summary available'}</p>
                        <div class="source-meta">
                            <span>🔗 <a href="${thread.url}" target="_blank">View on Reddit</a></span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Render expert opinions
     */
    renderExpertOpinions(opinions) {
        if (!opinions || opinions.length === 0) {
            return '<p>No expert opinions identified.</p>';
        }

        return `
            <div class="content-section">
                <h4>Expert Opinions (${opinions.length})</h4>
                ${opinions.map((opinion, index) => `
                    <div class="source-item expert-opinion">
                        <h5>Expert Insight #${index + 1}</h5>
                        <p><strong>Key Insight:</strong> ${opinion.insight || ''}</p>
                        <p><strong>Expertise Indicator:</strong> ${opinion.expertise_indicator || ''}</p>
                        <p><strong>Main Argument:</strong> ${opinion.argument || ''}</p>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Render community consensus
     */
    renderConsensus(consensus, crossReference) {
        const corroborated = crossReference?.corroborated_facts || [];
        const contradictions = crossReference?.contradictions || [];

        return `
            <div class="content-section">
                <h4>Community Consensus Analysis</h4>
                <div class="consensus-analysis">
                    <p><strong>Overall Sentiment:</strong> ${consensus.sentiment || 'neutral'}</p>
                    <p><strong>Agreement Level:</strong> ${consensus.agreement_level || 'unknown'}</p>

                    ${consensus.themes && consensus.themes.length > 0 ? `
                        <div class="themes-section">
                            <strong>Key Themes:</strong>
                            <ul>
                                ${consensus.themes.map(theme => `<li>${theme}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    ${consensus.majority_opinion ? `
                        <p><strong>Majority Opinion:</strong><br>${consensus.majority_opinion}</p>
                    ` : ''}

                    ${consensus.minority_opinions && consensus.minority_opinions.length > 0 ? `
                        <div class="minority-section">
                            <strong>Minority/Contrarian Views:</strong>
                            <ul>
                                ${consensus.minority_opinions.map(op => `<li>${op}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>

                ${corroborated.length > 0 ? `
                    <h4>Corroborated Facts</h4>
                    <ul>
                        ${corroborated.map(fact => `<li>${fact}</li>`).join('')}
                    </ul>
                ` : ''}

                ${contradictions.length > 0 ? `
                    <h4>Contradictions & Debates</h4>
                    <ul>
                        ${contradictions.map(contradiction => `<li>${contradiction}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render all sources/citations
     */
    renderAllSources(sources) {
        if (!sources || sources.length === 0) {
            return '<p>No sources available.</p>';
        }

        const webSources = sources.filter(s => s.type === 'web');
        const redditSources = sources.filter(s => s.type === 'reddit');

        return `
            <div class="content-section">
                ${webSources.length > 0 ? `
                    <h4>Web Sources (${webSources.length})</h4>
                    <ol>
                        ${webSources.map(source => `
                            <li>
                                <strong>${source.title || 'Untitled'}</strong><br>
                                <a href="${source.url}" target="_blank">${source.url}</a>
                            </li>
                        `).join('')}
                    </ol>
                ` : ''}

                ${redditSources.length > 0 ? `
                    <h4>Reddit Sources (${redditSources.length})</h4>
                    <ol>
                        ${redditSources.map(source => `
                            <li>
                                <strong>${source.title || 'Untitled'}</strong><br>
                                <a href="${source.url}" target="_blank">${source.url}</a>
                            </li>
                        `).join('')}
                    </ol>
                ` : ''}
            </div>
        `;
    },

    /**
     * Format markdown-like text to HTML
     */
    formatMarkdown(text) {
        if (!text) return '';

        // Simple markdown formatting
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    },

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('results-container');
        container.style.display = 'block';
        container.innerHTML = `
            <div class="error-message" style="padding: 20px; background: #fee; border: 2px solid #c00; border-radius: 8px; color: #c00;">
                <h3>❌ Error</h3>
                <p>${message}</p>
            </div>
        `;
    },

    /**
     * Reset all UI elements
     */
    reset() {
        // Hide all sections
        document.getElementById('progress-tracker').style.display = 'none';
        document.getElementById('discoveries-feed').style.display = 'none';
        document.getElementById('results-container').style.display = 'none';

        // Reset stages
        const stages = document.querySelectorAll('.stage');
        stages.forEach(stage => {
            const status = stage.querySelector('.status');
            status.textContent = 'pending';
            status.className = 'status pending';
            stage.classList.remove('active');
        });

        // Clear discoveries
        document.getElementById('live-updates').innerHTML = '';

        // Clear tab content
        document.getElementById('tab-content').innerHTML = '';
    }
};

// Export for use in other files
window.UI = UI;
