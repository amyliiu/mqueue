"use client";
import { useState, FormEvent, useEffect } from 'react';
import styles from './badminton-queue.module.css';

const API_URL = process.env.BACKEND_API_URL;
console.log(API_URL);

function getOrdinalSuffix(position: number): string {
  const j = position % 10;
  const k = position % 100;
  if (j === 1 && k !== 11) return "st";
  if (j === 2 && k !== 12) return "nd";
  if (j === 3 && k !== 13) return "rd";
  return "th";
}

function generateQueueItems(position: number) {
  const items = [];
  
  // Generate items only up to and including user's position
  for (let i = 0; i < position; i++) {
    items.push({
      name: i === position - 1 ? 'You' : 'Anonymous',
      isCurrent: i === position - 1
    });
  }
  
  return items;
}

export default function BadmintonQueue() {
  const [isLoading, setIsLoading] = useState(false);
  const [showQueueStatus, setShowQueueStatus] = useState(false);
  const [queuePosition, setQueuePosition] = useState<number | null>(null);
  const [queueItems, setQueueItems] = useState<Array<{ name: string, isCurrent: boolean }>>([]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (showQueueStatus && queuePosition) {
      // Initial fetch
      fetchQueueStatus();

      // Set up polling every 5 seconds
      intervalId = setInterval(fetchQueueStatus, 5000);
    }

    // Cleanup on unmount or when showQueueStatus changes
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [showQueueStatus, queuePosition]);

  async function fetchQueueStatus() {
    try {
      const response = await fetch(`${API_URL}/api/v1/queue`);
      const data = await response.json();
      
      if (response.ok && data && Array.isArray(data.queue)) {
        // Check if we're still in the queue
        const stillInQueue = data.queue.some((player: any) => 
          player.position === queuePosition
        );

        if (!stillInQueue) {
          setShowQueueStatus(false);
          return;
        }

        // Update queue items
        const items = [];
        for (let i = 0; i < queuePosition!; i++) {
          items.push({
            name: i === queuePosition! - 1 ? 'You' : 'Anonymous',
            isCurrent: i === queuePosition! - 1
          });
        }
        setQueueItems(items);
      }
    } catch (error) {
      console.error('Error fetching queue status:', error);
    }
  }

  async function addToQueue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);

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

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to add to queue');
      }

      const position = data.position;
      setQueuePosition(position);
      setQueueItems(generateQueueItems(position));
      setShowQueueStatus(true);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      {showQueueStatus ? (
        <div className={styles.queueStatusContainer}>
          <div className={styles.queueStatus}>
            <div className={styles.queueHeader}>You are</div>
            <div className={styles.positionDisplay}>
              {queuePosition}{getOrdinalSuffix(queuePosition!)}
            </div>
            <div className={styles.queueHeader}>in the Queue!</div>
            
            <div className={styles.menuList}>
              {queueItems.map((item, index) => (
                <div 
                  key={index}
                  className={`${styles.menuItem} ${item.isCurrent ? styles.activeMenuItem : ''}`}
                >
                  {item.name}
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          <h1 className={styles.title}>MQueue</h1>
          <form onSubmit={addToQueue} className={styles.queueForm}>
            <input
              type="text"
              name="name"
              className={styles.inputField}
              placeholder="Name *"
              required
            />
            <input
              type="tel"
              name="phoneNumber"
              className={styles.inputField}
              placeholder="Phone Number *"
              required
            />
            <div className={styles.checkboxContainer}>
              <input type="checkbox" id="consent" required />
              <label htmlFor="consent">
                By providing your information you opt in to receiving texts from our service. 
                Messaging rates may apply.
              </label>
            </div>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading}
            >
              {isLoading ? 'Adding...' : 'Add to Queue'}
            </button>
          </form>
        </>
      )}
    </div>
  );
}