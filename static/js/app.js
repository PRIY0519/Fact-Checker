// Holy Books Facts Checker - Frontend JavaScript
class FactsCheckerApp {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentResult = null;
        this.speechSynthesis = window.speechSynthesis;
        
        this.initializeEventListeners();
        this.loadHistory();
    }

    initializeEventListeners() {
        // Submit button
        document.getElementById('submit-btn').addEventListener('click', () => {
            this.submitFactCheck();
        });

        // Voice input button
        document.getElementById('voice-btn').addEventListener('click', () => {
            this.toggleVoiceRecording();
        });

        // Claim type buttons
        document.querySelectorAll('.claim-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectClaimType(e.target);
            });
        });

        // Source filter buttons
        document.querySelectorAll('.source-filter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterSources(e.target.dataset.filter);
            });
        });

        // History toggle
        document.getElementById('history-toggle').addEventListener('click', () => {
            this.toggleHistory();
        });

        // Accessibility toggle
        document.getElementById('accessibility-toggle').addEventListener('click', () => {
            this.toggleAccessibility();
        });

        // Action buttons
        document.getElementById('speak-result').addEventListener('click', () => {
            this.speakResult();
        });

        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportPDF();
        });

        document.getElementById('export-json').addEventListener('click', () => {
            this.exportJSON();
        });

        // File upload
        document.getElementById('file-upload').addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });

        // Enter key in textarea
        document.getElementById('claim-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.submitFactCheck();
            }
        });

        // Drag and drop for file upload
        const dropZone = document.querySelector('.border-dashed');
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload({ target: { files } });
            }
        });
    }

    async submitFactCheck() {
        const claim = document.getElementById('claim-input').value.trim();
        const language = document.getElementById('language-select').value;
        const claimType = document.querySelector('.claim-type-btn.active').dataset.type;

        if (!claim) {
            this.showToast('Please enter a claim to check', 'error');
            return;
        }

        this.showLoadingState();

        try {
            const response = await fetch('/api/fact-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    claim: claim,
                    language: language,
                    claim_type: claimType
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayResults(result);
                this.currentResult = result;
                this.loadHistory(); // Refresh history
            } else {
                throw new Error(result.error || 'Failed to check facts');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message, 'error');
            this.hideLoadingState();
        }
    }

    async toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support audio recording or microphone access. Please use a modern browser (Chrome, Edge, Firefox) and ensure you are running on HTTPS or localhost.");
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            this.isRecording = true;
            this.mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) this.audioChunks.push(event.data);
            };
            this.mediaRecorder.start();
            this.updateVoiceButton(true);
            this.showWaveform(true);
        } catch (err) {
            console.error("Error starting recording:", err);
            alert("Could not start audio recording: " + err.message);
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.processAudio(audioBlob);
            };
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.updateVoiceButton(false);
            this.showWaveform(false);
        }
    }

    async processAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);

        try {
            const response = await fetch('/api/speech-to-text', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                document.getElementById('claim-input').value = result.text;
                this.showToast('Voice input processed successfully', 'success');
            } else {
                throw new Error(result.error || 'Failed to process audio');
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            this.showToast('Could not process voice input', 'error');
        }
    }

    updateVoiceButton(isRecording) {
        const btn = document.getElementById('voice-btn');
        const text = document.getElementById('voice-text');
        const icon = btn.querySelector('i');

        if (isRecording) {
            btn.classList.remove('from-blue-500', 'to-purple-600');
            btn.classList.add('from-red-500', 'to-red-600');
            text.textContent = 'Stop Recording';
            icon.className = 'fas fa-stop text-xl';
        } else {
            btn.classList.remove('from-red-500', 'to-red-600');
            btn.classList.add('from-blue-500', 'to-purple-600');
            text.textContent = 'Start Voice Input';
            icon.className = 'fas fa-microphone text-xl';
        }
    }

    showWaveform(show) {
        const waveform = document.getElementById('waveform');
        if (show) {
            waveform.classList.remove('hidden');
        } else {
            waveform.classList.add('hidden');
        }
    }

    animateWaveform() {
        if (!this.isRecording) return;

        const bars = document.querySelectorAll('.waveform-bar');
        bars.forEach(bar => {
            const height = Math.random() * 30 + 5;
            bar.style.height = `${height}px`;
        });

        setTimeout(() => this.animateWaveform(), 100);
    }

    selectClaimType(selectedBtn) {
        document.querySelectorAll('.claim-type-btn').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
            btn.classList.add('border-gray-300', 'text-gray-600');
        });

        selectedBtn.classList.add('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
        selectedBtn.classList.remove('border-gray-300', 'text-gray-600');
    }

    filterSources(filter) {
        document.querySelectorAll('.source-filter').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
            btn.classList.add('border-gray-300', 'text-gray-600');
        });

        const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
        activeBtn.classList.add('active', 'border-blue-500', 'bg-blue-50', 'text-blue-700');
        activeBtn.classList.remove('border-gray-300', 'text-gray-600');

        // Filter sources display (implement based on your data structure)
        this.updateSourcesDisplay(filter);
    }

    updateSourcesDisplay(filter) {
        const container = document.getElementById('sources-container');
        
        if (!this.currentResult || !this.currentResult.citations) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-book-open text-2xl mb-2"></i>
                    <p>Sources will appear here after fact checking</p>
                </div>
            `;
            return;
        }

        let sources = this.currentResult.citations;
        
        if (filter !== 'all') {
            // Filter sources based on type (implement based on your data structure)
            sources = sources.filter(source => source.type === filter);
        }

        if (sources.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-filter text-2xl mb-2"></i>
                    <p>No ${filter} sources found</p>
                </div>
            `;
            return;
        }

        container.innerHTML = sources.map(source => `
            <div class="bg-gray-50 rounded-lg p-3 border-l-4 border-blue-500">
                <div class="font-medium text-sm text-gray-800">${source.work || 'Unknown Source'}</div>
                <div class="text-xs text-gray-600 mt-1">${source.reference || ''}</div>
                <div class="text-sm text-gray-700 mt-2 italic">"${source.text || ''}"</div>
            </div>
        `).join('');
    }

    displayResults(result) {
        this.hideLoadingState();
        this.currentResult = result;

        // Show results content and hide initial state
        document.getElementById('initial-state').classList.add('hidden');
        document.getElementById('results-content').classList.remove('hidden');

        // Update enhanced verdict card
        const verdictCard = document.getElementById('verdict-card');
        const verdictIcon = document.getElementById('verdict-icon');
        const verdictStatus = document.getElementById('verdict-status');
        const verdictSubtitle = document.getElementById('verdict-subtitle');
        const verdictBadge = document.getElementById('verdict-badge');

        // Set verdict card styling and content
        const verdictInfo = this.getVerdictInfo(result.verdict);
        verdictCard.className = `rounded-xl p-6 text-white text-center mb-4 shadow-lg pulse-glow verdict-${result.verdict.toLowerCase().replace(' ', '-')}`;
        verdictIcon.className = `${verdictInfo.icon} text-4xl mr-3`;
        verdictStatus.textContent = verdictInfo.status;
        verdictSubtitle.textContent = verdictInfo.subtitle;
        verdictBadge.textContent = result.verdict;

        // Update enhanced confidence display
        const confidenceText = document.getElementById('confidence-text');
        const confidenceBar = document.getElementById('confidence-bar');
        const confidenceDescription = document.getElementById('confidence-description');
        
        confidenceText.textContent = `${result.confidence}%`;
        confidenceBar.style.width = `${result.confidence}%`;
        
        const confidenceInfo = this.getConfidenceInfo(result.confidence);
        confidenceBar.className = `h-4 rounded-full transition-all duration-1000 relative overflow-hidden ${confidenceInfo.class}`;
        confidenceDescription.textContent = confidenceInfo.description;

        // Update rationale
        document.getElementById('rationale-content').textContent = result.rationale;

        // Update citations
        this.updateCitationsDisplay(result.citations);

        // Update alternative views
        if (result.alternative_views && result.alternative_views.length > 0) {
            document.getElementById('alternative-views').classList.remove('hidden');
            document.getElementById('alternative-views-content').innerHTML = 
                result.alternative_views.map(view => `<p class="mb-2">• ${view}</p>`).join('');
        } else {
            document.getElementById('alternative-views').classList.add('hidden');
        }

        // Update next steps
        const nextStepsContainer = document.getElementById('next-steps-container');
        if (result.next_steps && result.next_steps.length > 0) {
            nextStepsContainer.innerHTML = result.next_steps.map(step => 
                `<div class="flex items-start space-x-2">
                    <i class="fas fa-arrow-right text-blue-500 mt-1 text-sm"></i>
                    <span class="text-sm text-gray-700">${step}</span>
                </div>`
            ).join('');
        }

        // Show results
        document.getElementById('initial-state').classList.add('hidden');
        document.getElementById('results-content').classList.remove('hidden');

        // Update sources
        this.updateSourcesDisplay('all');
    }

    updateCitationsDisplay(citations) {
        const container = document.getElementById('citations-container');
        
        if (!citations || citations.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm">No citations available</p>';
            return;
        }

        container.innerHTML = citations.map(citation => `
            <div class="bg-gray-50 rounded-lg p-3 border-l-4 border-green-500">
                <div class="font-medium text-sm text-gray-800">${citation.work || 'Unknown Source'}</div>
                <div class="text-xs text-gray-600 mt-1">${citation.reference || ''}</div>
                <div class="text-sm text-gray-700 mt-2 italic">"${citation.text || ''}"</div>
            </div>
        `).join('');
    }

    getVerdictInfo(verdict) {
        const verdictMap = {
            'Supported': {
                status: 'FACT VERIFIED ✓',
                subtitle: 'This claim is supported by scripture',
                icon: 'fas fa-check-circle'
            },
            'Contradicted': {
                status: 'FACT DISPUTED ✗',
                subtitle: 'This claim contradicts scripture',
                icon: 'fas fa-times-circle'
            },
            'Partially supported': {
                status: 'PARTIALLY CORRECT ⚠',
                subtitle: 'This claim has mixed support',
                icon: 'fas fa-exclamation-triangle'
            },
            'Unclear': {
                status: 'UNCLEAR EVIDENCE ?',
                subtitle: 'Insufficient evidence to verify',
                icon: 'fas fa-question-circle'
            },
            'Theological': {
                status: 'THEOLOGICAL MATTER ⚡',
                subtitle: 'This involves matters of faith',
                icon: 'fas fa-praying-hands'
            }
        };
        return verdictMap[verdict] || verdictMap['Unclear'];
    }

    getConfidenceInfo(confidence) {
        if (confidence >= 85) {
            return {
                class: 'confidence-excellent',
                description: 'Excellent confidence - Very reliable result'
            };
        } else if (confidence >= 70) {
            return {
                class: 'confidence-good',
                description: 'Good confidence - Reliable result'
            };
        } else if (confidence >= 50) {
            return {
                class: 'confidence-moderate',
                description: 'Moderate confidence - Consider additional sources'
            };
        } else {
            return {
                class: 'confidence-low',
                description: 'Low confidence - Requires further verification'
            };
        }
    }

    getConfidenceColor(confidence) {
        if (confidence >= 80) return 'bg-green-500';
        if (confidence >= 60) return 'bg-yellow-500';
        if (confidence >= 40) return 'bg-orange-500';
        return 'bg-red-500';
    }

    showLoadingState() {
        document.getElementById('initial-state').classList.add('hidden');
        document.getElementById('results-content').classList.add('hidden');
        document.getElementById('loading-state').classList.remove('hidden');
    }

    hideLoadingState() {
        document.getElementById('loading-state').classList.add('hidden');
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history?limit=5');
            const history = await response.json();

            if (response.ok) {
                this.displayHistory(history);
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    displayHistory(history) {
        const container = document.getElementById('history-container');
        
        if (!history || history.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm">No recent checks</p>';
            return;
        }

        container.innerHTML = history.map(item => `
            <div class="bg-gray-50 rounded-lg p-3 cursor-pointer hover:bg-gray-100 transition-colors" 
                 onclick="app.loadHistoryItem('${item.claim}')">
                <div class="font-medium text-sm text-gray-800 truncate">${item.claim}</div>
                <div class="flex items-center justify-between mt-2">
                    <span class="px-2 py-1 rounded-full text-xs text-white verdict-${item.verdict.toLowerCase().replace(' ', '-')}">
                        ${item.verdict}
                    </span>
                    <span class="text-xs text-gray-500">${this.formatDate(item.timestamp)}</span>
                </div>
            </div>
        `).join('');
    }

    loadHistoryItem(claim) {
        document.getElementById('claim-input').value = claim;
        this.showToast('Claim loaded from history', 'info');
    }

    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    toggleHistory() {
        const panel = document.getElementById('history-panel');
        panel.classList.toggle('hidden');
    }

    toggleAccessibility() {
        document.body.classList.toggle('accessibility-font');
        this.showToast('Accessibility mode toggled', 'info');
    }

    speakResult() {
        if (!this.currentResult) {
            this.showToast('No result to speak', 'error');
            return;
        }

        const text = `
            Verdict: ${this.currentResult.verdict}. 
            Confidence: ${this.currentResult.confidence} percent. 
            ${this.currentResult.rationale}
        `;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        this.speechSynthesis.speak(utterance);

        this.showToast('Speaking result...', 'info');
    }

    exportPDF() {
        if (!this.currentResult) {
            this.showToast('No result to export', 'error');
            return;
        }

        // Simple PDF export using browser print
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Fact Check Report</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .header { text-align: center; margin-bottom: 30px; }
                        .section { margin-bottom: 20px; }
                        .verdict { font-weight: bold; color: #2563eb; }
                        .confidence { color: #059669; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Holy Books Facts Checker Report</h1>
                        <p>Generated on ${new Date().toLocaleString()}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Claim</h2>
                        <p>${this.currentResult.claim}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Verdict</h2>
                        <p class="verdict">${this.currentResult.verdict}</p>
                        <p class="confidence">Confidence: ${this.currentResult.confidence}%</p>
                    </div>
                    
                    <div class="section">
                        <h2>Rationale</h2>
                        <p>${this.currentResult.rationale}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Citations</h2>
                        ${this.currentResult.citations.map(citation => `
                            <div style="margin-bottom: 10px; padding: 10px; border-left: 3px solid #2563eb; background: #f8fafc;">
                                <strong>${citation.work || 'Unknown Source'}</strong><br>
                                <em>${citation.reference || ''}</em><br>
                                "${citation.text || ''}"
                            </div>
                        `).join('')}
                    </div>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    exportJSON() {
        if (!this.currentResult) {
            this.showToast('No result to export', 'error');
            return;
        }

        const dataStr = JSON.stringify(this.currentResult, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `fact-check-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showToast('JSON exported successfully', 'success');
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target.result;
            document.getElementById('claim-input').value = text;
            this.showToast('File uploaded successfully', 'success');
        };
        reader.readAsText(file);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        toast.className = `${colors[type]} text-white px-4 py-2 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
        toast.textContent = message;

        container.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FactsCheckerApp();
});
