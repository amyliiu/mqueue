"use client";
import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

export default function BadmintonQueue() {
  const [queue, setQueue] = useState<Array<{ name: string; phoneNumber: string }>>([]);
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
    getQueue();
  }, []);

  async function getQueue() {
    try {
      const response = await fetch(`${API_URL}/api/v1/queue`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setQueue(data);
    } catch (error) {
      console.error('Error fetching queue:', error);
      setQueue([]);
    }
  }

  // ... other imports and initial code remain the same ...

async function addToQueue(event: React.FormEvent<HTMLFormElement>) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const name = formData.get('name') as string;
  const phoneNumber = formData.get('phoneNumber') as string;

  try {
    const response = await fetch(`${API_URL}/api/v1/queue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, phoneNumber }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message || 
        `Failed to add player to queue. Status: ${response.status}`
      );
    }

    form.reset();
    await getQueue();
    //event.currentTarget.reset();
    // ^^ does this line need to be there? it works when its commented out

  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error('Error adding player to queue:', error.message);
    } else {
      console.error('Error adding player to queue:', String(error));
    }
  }
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