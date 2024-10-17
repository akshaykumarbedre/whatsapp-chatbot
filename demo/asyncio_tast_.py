import asyncio

# Define an asynchronous function
async def my_async_task(name, delay):
    print(f"Task {name} started, it will take {delay} seconds.")
    await asyncio.sleep(delay)  # Simulate an I/O-bound task with asyncio.sleep
    print(f"Task {name} completed.")
    return f"Result from {name}"

# Main function to run multiple tasks concurrently
async def main():
    # Schedule multiple asynchronous tasks
    task1 = asyncio.create_task(my_async_task("Task 1", 2))  # Takes 2 seconds
    task2 = asyncio.create_task(my_async_task("Task 2", 3))  # Takes 3 seconds
    task3 = asyncio.create_task(my_async_task("Task 3", 1))  # Takes 1 second

    # Wait for all tasks to complete
    results = await asyncio.gather(task1, task2, task3)
    
    # Print the results of each task
    print(f"All tasks completed: {results}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
