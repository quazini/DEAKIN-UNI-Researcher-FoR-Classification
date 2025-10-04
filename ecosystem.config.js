/**
 * PM2 Ecosystem Configuration for FoR Classification System
 *
 * Usage:
 * - Start: pm2 start ecosystem.config.js
 * - Restart: pm2 restart for-classification
 * - Stop: pm2 stop for-classification
 * - Logs: pm2 logs for-classification
 * - Monitor: pm2 monit
 */

module.exports = {
  apps: [{
    name: 'for-classification',
    script: 'streamlit',
    args: 'run login.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true',
    interpreter: 'none',

    // Working directory
    cwd: './',

    // Environment variables
    env: {
      // Add .local/bin to PATH so PM2 can find streamlit
      PATH: '/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',

      // Streamlit configuration
      STREAMLIT_SERVER_PORT: '8501',
      STREAMLIT_SERVER_ADDRESS: '0.0.0.0',
      STREAMLIT_SERVER_HEADLESS: 'true',
      STREAMLIT_BROWSER_GATHER_USAGE_STATS: 'false',
      STREAMLIT_SERVER_MAX_UPLOAD_SIZE: '50',

      // Application settings
      APP_NAME: 'FoR Classification System',
      APP_ENV: 'production',
      SESSION_TIMEOUT_MINUTES: '60',

      // Note: Sensitive values (SUPABASE_URL, SUPABASE_KEY, NEO4J_*, etc.)
      // should be set in a .env file, not here in version control
    },

    // Process management
    instances: 1,
    exec_mode: 'fork',

    // Restart policy
    autorestart: true,
    watch: false,  // Don't auto-restart on file changes (use pm2 restart for deployments)
    max_memory_restart: '1G',  // Restart if memory exceeds 1GB

    // Logging
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,  // Prefix logs with timestamps
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

    // Advanced options
    min_uptime: '10s',  // Consider app online after 10 seconds
    max_restarts: 10,   // Max restarts within 1 minute before giving up
    restart_delay: 4000,  // Delay between restarts (ms)

    // Environment-specific settings
    env_production: {
      NODE_ENV: 'production',
      APP_ENV: 'production'
    },

    env_development: {
      NODE_ENV: 'development',
      APP_ENV: 'development',
      STREAMLIT_SERVER_HEADLESS: 'false'
    }
  }]
};
