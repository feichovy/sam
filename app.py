from flask import Flask, render_template, request, jsonify
from router_configurator import RouterConfigurator
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def configure_router():
    try:
        # Get form data
        ip = request.form.get('router_ip')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Custom commands (optional)
        custom_commands = request.form.get('custom_commands', '').split('\n')
        custom_commands = [cmd.strip() for cmd in custom_commands if cmd.strip()]
        
        # Use default commands if no custom commands provided
        commands = custom_commands if custom_commands else RouterConfigurator.get_default_commands()
        
        # Configure router
        router = RouterConfigurator(ip, username, password)
        success = router.configure_router(commands)
        
        return jsonify({
            'success': success,
            'message': 'Router configured successfully!' if success else 'Configuration failed. Check logs.'
        })
    
    except Exception as e:
        app.logger.error(f"Configuration error: {e}")
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)