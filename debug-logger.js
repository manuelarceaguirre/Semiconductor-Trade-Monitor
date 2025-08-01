// Robust file logging system - writes directly to server file
class DebugLogger {
    constructor() {
        this.logs = [];
        this.logCount = 0;
        this.startTime = Date.now();
        
        // Log immediately to show the system is working
        this.log('🚀 DEBUG LOGGER INITIALIZED');
        
        // Set up periodic flushing to file
        setInterval(() => this.flushLogs(), 1000);
    }
    
    log(message) {
        this.logCount++;
        const timestamp = new Date().toISOString();
        const logEntry = `[${this.logCount}] ${timestamp} | ${message}`;
        
        console.log(logEntry); // Still show in console
        this.logs.push(logEntry);
        
        // Immediate flush for important messages
        if (message.includes('ERROR') || message.includes('FAIL')) {
            this.flushLogs();
        }
    }
    
    flushLogs() {
        if (this.logs.length === 0) return;
        
        const logsToSend = [...this.logs];
        this.logs = [];
        
        fetch('/write-debug-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                logs: logsToSend,
                timestamp: new Date().toISOString(),
                sessionStart: this.startTime
            })
        }).catch(error => {
            console.error('Failed to write logs to file:', error);
            // Put logs back if failed
            this.logs = logsToSend.concat(this.logs);
        });
    }
    
    error(message) {
        this.log(`❌ ERROR: ${message}`);
    }
    
    success(message) {
        this.log(`✅ SUCCESS: ${message}`);
    }
    
    info(message) {
        this.log(`ℹ️ INFO: ${message}`);
    }
}

// Create global logger instance
window.logger = new DebugLogger();