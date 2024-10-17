from flask import Flask, jsonify
import asyncio

# Create a Flask app
app = Flask(__name__)

# Define an asynchronous function (e.g., simulate an I/O-bound task)
async def async_task():
    print("Async task started...")
    await asyncio.sleep(3)  # Simulate a long-running task
    print("Async task completed!")
    return "Task finished!"

# Define a route that triggers an asynchronous task
@app.route('/run_async_task', methods=['GET'])
async def run_async_task():
    result = await async_task()  # Run the async function
    return jsonify({'status': 'success', 'message': result}), 200

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
