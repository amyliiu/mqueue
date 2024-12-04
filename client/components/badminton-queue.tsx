"use client";
import { useState, FormEvent, useEffect } from 'react';
import styles from './badminton-queue.module.css';

// const API_URL = "http://localhost:8000"
const API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;
console.log(API_URL);
if (!API_URL) {
  console.error('NEXT_PUBLIC_BACKEND_API_URL is not defined');
}
function getOrdinalSuffix(position: number): string {
  const j = position % 10;
  const k = position % 100;
  if (j === 1 && k !== 11) return "st";
  if (j === 2 && k !== 12) return "nd";
  if (j === 3 && k !== 13) return "rd";
  return "th";
}

function generateQueueItems(position: number, groupSize: number | null) {
  const items = [];

  for (let i = 0; i < position; i++) {
    items.push({
      name: i === position - 1 ? `you (${groupSize})` : 'anonymous',
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
  const [groupSize, setGroupSize] = useState<number | null>(null);
  const [phoneNumber, setPhoneNumber] = useState<string | null>(null);

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
        console.log('Current Queue:', data.queue);
        console.log('Current Queue Position:', queuePosition);

        // Check if we're still in the queue by phone number
        const stillInQueue = data.queue.some((player: any) => 
          player.phoneNumber === phoneNumber
        );

        if (!stillInQueue) {
          setShowQueueStatus(false);
          return;
        }

        const items = generateQueueItems(queuePosition!, groupSize);
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
    const phoneNumberInput = formData.get('phoneNumber') as string;

    setPhoneNumber(phoneNumberInput);

    try {
      const response = await fetch(`${API_URL}/api/v1/add-to-queue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phoneNumber: phoneNumberInput, groupSize }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to add to queue');
      }

      const position = data.position;
      setQueuePosition(position);
      setQueueItems(generateQueueItems(position, groupSize));
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
            <div className={styles.queueHeader}>you are</div>
            <div className={styles.positionDisplay}>
              {queuePosition}{getOrdinalSuffix(queuePosition!)}
            </div>
            <div className={styles.queueHeader}>in the queue!</div>
            
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
          <h1 className={styles.title}>
            <span style={{ color: 'white' }}>court</span>
            <span>line</span>
          </h1>
          <form onSubmit={addToQueue} className={styles.queueForm}>
            <input
              type="text"
              name="name"
              className={styles.inputField}
              placeholder="name *"
              required
            />
            <input
              type="tel"
              name="phoneNumber"
              className={styles.inputField}
              placeholder="phone number *"
              required
            />
            <input
              type="number"
              name="groupSize"
              className={styles.inputField}
              placeholder="group size *"
              required
              onChange={(e) => setGroupSize(Number(e.target.value))}
            />
            <div className={styles.checkboxContainer}>
              <input type="checkbox" id="consent" className={styles.checkbox} required />
              <label htmlFor="consent" className={styles.checkboxLabel}>
                by providing your information you opt in to receiving texts from our service. 
                messaging rates may apply.
              </label>
            </div>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading}
            >
              {isLoading ? 'adding...' : 'add to queue'}
            </button>
          </form>
        </>
      )}
    </div>
  );
}