"use client";
import { useState, useEffect, FormEvent } from 'react';

const API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

export default function BadmintonQueue() {
  const [queue, setQueue] = useState<Array<{ name: string; phoneNumber: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showQueueStatus, setShowQueueStatus] = useState(false);
  const [queuePosition, setQueuePosition] = useState(0);

  useEffect(() => {
    getQueue();
  }, []);

  const getNumberSuffix = (number: number) => {
    const j = number % 10;
    const k = number % 100;
    if (j === 1 && k !== 11) return "st";
    if (j === 2 && k !== 12) return "nd";
    if (j === 3 && k !== 13) return "rd";
    return "th";
  };

  async function getQueue() {
    try {
      const response = await fetch(`${API_URL}/api/v1/queue`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setQueue(data);
    } catch (error) {
      console.error('Error fetching queue:', error);
      setQueue([]);
    }
  }
  async function addToQueue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
  
    const form = event.currentTarget;
    const formData = new FormData(form);
    const name = formData.get('name') as string;
    let phoneNumber = formData.get('phoneNumber') as string;
  
    try {
      if (name.length < 2) {
        throw new Error('Name must be at least 2 characters long');
      }
  
      phoneNumber = phoneNumber.replace(/\D/g, '');
      if (phoneNumber.length === 10) {
        phoneNumber = `+1${phoneNumber}`;
      } else if (phoneNumber.length === 11 && phoneNumber.startsWith('1')) {
        phoneNumber = `+${phoneNumber}`;
      } else {
        throw new Error('Please enter a valid 10-digit phone number');
      }

      console.log('Form values:', {
        name: formData.get('name'),
        phoneNumber: formData.get('phoneNumber')
    });

      const response = await fetch(`${API_URL}/api/v1/queue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phoneNumber }),
      });
  
      const data = await response.json();
      
      if (!response.ok) {
        // Handle the error response from the server properly
        throw new Error(data.detail || JSON.stringify(data) || 'Failed to add to queue');
      }
  
      await getQueue();
      setQueuePosition(data.position);
      setShowQueueStatus(true);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  }
  
  // Update your form input
  return (
    <div className="container">
      <h1 className="title">MQueue</h1>
      <form onSubmit={addToQueue} className="queue-form">
        <input
          type="text"
          name="name"
          className="input-field"
          placeholder="Name *"
          pattern="[A-Za-z\s-]+"
          title="Name can only contain letters, spaces, and hyphens"
          required
          minLength={2}
        />
        <input
          type="tel"
          name="phoneNumber"
          className="input-field"
          placeholder="Phone Number * (e.g., 1234567890)"
          pattern="^\+?1?\d{10}$"
          title="Please enter a valid 10-digit phone number"
          required
        />
        <div className="checkbox-container">
          <input type="checkbox" id="consent" required />
          <label htmlFor="consent">
            By providing your information you opt in to receiving texts from our service. 
            Messaging rates may apply.
          </label>
        </div>
        <button
          type="submit"
          className="submit-button"
          disabled={isLoading}
        >
          {isLoading ? 'Adding...' : 'Add to Queue'}
        </button>
      </form>
    </div>
  );
}