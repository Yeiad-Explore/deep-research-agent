/**
 * API Communication Layer
 * Handles all communication with the backend
 */

class ResearchAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.ws = null;
        this.currentSessionId = null;
    }

    /**
     * Start research using WebSocket for streaming
     */
    async startResearchStream(query, config) {
        return new Promise((resolve, reject) => {
            // Construct WebSocket URL
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsURL = `${wsProtocol}//${window.location.host}/ws/research`;

            console.log('Connecting to WebSocket:', wsURL);
            this.ws = new WebSocket(wsURL);

            this.ws.onopen = () => {
                console.log('WebSocket connected');

                // Send research request
                const request = {
                    query: query,
                    config: config
                };

                this.ws.send(JSON.stringify(request));
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message:', data);

                    // Emit custom event for UI updates
                    window.dispatchEvent(new CustomEvent('research-update', {
                        detail: data
                    }));

                    // If complete, resolve the promise
                    if (data.status === 'complete') {
                        this.currentSessionId = data.session_id;
                        resolve(data.result);
                    } else if (data.status === 'error') {
                        reject(new Error(data.message));
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket closed');
            };
        });
    }

    /**
     * Start research using regular HTTP POST (fallback)
     */
    async startResearch(query, config) {
        try {
            const response = await fetch(`${this.baseURL}/api/research`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    config: config
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentSessionId = data.session_id;
            return data;
        } catch (error) {
            console.error('Error starting research:', error);
            throw error;
        }
    }

    /**
     * Get research session by ID
     */
    async getResearch(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/research/${sessionId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting research:', error);
            throw error;
        }
    }

    /**
     * Refine existing research
     */
    async refineResearch(sessionId, refinementQuery, addSources = null) {
        try {
            const response = await fetch(`${this.baseURL}/api/research/${sessionId}/refine`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refinement_query: refinementQuery,
                    add_sources: addSources
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error refining research:', error);
            throw error;
        }
    }

    /**
     * Discover subreddits for a topic
     */
    async discoverSubreddits(topic, limit = 10) {
        try {
            const params = new URLSearchParams({
                topic: topic,
                limit: limit.toString()
            });

            const response = await fetch(`${this.baseURL}/api/subreddits/discover?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error discovering subreddits:', error);
            throw error;
        }
    }

    /**
     * Analyze a specific Reddit thread
     */
    async analyzeThread(threadUrl, depth = 'full') {
        try {
            const params = new URLSearchParams({
                thread_url: threadUrl,
                depth: depth
            });

            const response = await fetch(`${this.baseURL}/api/reddit/analyze-thread?${params}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error analyzing thread:', error);
            throw error;
        }
    }

    /**
     * Close WebSocket connection
     */
    closeWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Export for use in other files
window.ResearchAPI = ResearchAPI;
