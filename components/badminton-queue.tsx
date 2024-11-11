"use client";
import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

export default function BadmintonQueue() {
  const [queue, setQueue] = useState<Array<{ name: string; phoneNumber: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);  // Add loading state

  useEffect(() => {
    // Fetch queue data when component mounts
    getQueue();
  }, []);

  async function getQueue() {
    try {
      const response = await fetch(`${API_URL}/api/queue/get_queue`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setQueue(data);
    } catch (error) {
      console.error('Error fetching queue:', error);
      setQueue([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function addToQueue(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const name = formData.get('name') as string;
    const phoneNumber = formData.get('phoneNumber') as string;

    try {
      const response = await fetch(`${API_URL}/api/queue/add_to_queue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phoneNumber }),
      });

      if (!response.ok) {
        throw new Error('Failed to add player to queue');
      }

      // Refresh the queue after successful addition
      getQueue();
      
      // Reset the form
      event.currentTarget.reset();
    } catch (error) {
      console.error('Error adding player to queue:', error);
    }
  }

  // Show loading state
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Badminton Queue</h1>
      
      {/* Add to Queue Form */}
      <form onSubmit={addToQueue} className="mb-8">
        <div className="flex flex-col gap-4 max-w-md">
          <input
            type="text"
            name="name"
            placeholder="Name"
            required
            className="p-2 border rounded"
          />
          <input
            type="tel"
            name="phoneNumber"
            placeholder="Phone Number"
            required
            className="p-2 border rounded"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Add to Queue
          </button>
        </div>
      </form>

      {/* Queue Display */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Current Queue</h2>
        {queue.length === 0 ? (
          <p>No one in queue</p>
        ) : (
          <ul className="space-y-2">
            {queue.map((player, index) => (
              <li key={index} className="p-2 bg-gray-100 rounded">
                {player.name} - {player.phoneNumber}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
} 