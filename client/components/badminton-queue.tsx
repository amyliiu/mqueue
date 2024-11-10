'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Player = {
  name: string
  phoneNumber: string
}

export default function BadmintonQueue() {
  const [queue, setQueue] = useState<Player[]>([])
  const [currentPlayers, setCurrentPlayers] = useState<Player[]>([])
  const [playerName, setPlayerName] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [error, setError] = useState<string | null>(null) // For error handling

  // Function to add player to queue
  const addToQueue = (e: React.FormEvent) => {
    e.preventDefault()
    if (playerName.trim() && phoneNumber.trim()) {
      setQueue([...queue, { name: playerName.trim(), phoneNumber: phoneNumber.trim() }])
      setPlayerName('')
      setPhoneNumber('')
    }
  }

  // Function to start a game with the first 4 players in the queue
  const startGame = async () => {
    if (queue.length >= 4) {
      const newPlayers = queue.slice(0, 4)
      setCurrentPlayers(newPlayers)
      setQueue(queue.slice(4))

      // Send SMS notifications to players using the FastAPI backend
      try {
        for (const player of newPlayers) {
          const response = await fetch('http://localhost:8000/api/v1/send-sms', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              phoneNumber: player.phoneNumber,
              message: `Hi ${player.name}, your badminton game is starting now!`
            })
          })

          const data = await response.json()
          if (!response.ok) {
            throw new Error(data.message || `Failed to send SMS to ${player.phoneNumber}`)
          }
        }
        setError(null) // Clear any previous error messages on success
      } catch (err: any) {
        console.error(err)
        setError(`Failed to send SMS notifications: ${err.message}`)
      }
    }
  }

  // Function to end the current game
  const endGame = () => {
    setCurrentPlayers([])
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">MQueue</h1>
      
      {/* Display any error messages */}
      {error && <p className="text-red-500 mb-4">{error}</p>}
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Add Player to Queue</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={addToQueue} className="space-y-4">
            <div>
              <Input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Enter player name"
                className="w-full"
              />
            </div>
            <div>
              <Input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="Enter phone number"
                className="w-full"
              />
            </div>
            <Button type="submit" className="w-full">Add to Queue</Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Queue of players waiting to play */}
        <Card>
          <CardHeader>
            <CardTitle>Current Queue</CardTitle>
          </CardHeader>
          <CardContent>
            {queue.length > 0 ? (
              <ol className="list-decimal list-inside">
                {queue.map((player, index) => (
                  <li key={index} className="mb-1">{player.name}</li>
                ))}
              </ol>
            ) : (
              <p>No players in queue</p>
            )}
          </CardContent>
        </Card>

        {/* Current game in progress */}
        <Card>
          <CardHeader>
            <CardTitle>Current Game</CardTitle>
          </CardHeader>
          <CardContent>
            {currentPlayers.length === 4 ? (
              <>
                <p className="mb-4">
                  Team 1: {currentPlayers[0].name} & {currentPlayers[1].name}
                  <br />
                  Team 2: {currentPlayers[2].name} & {currentPlayers[3].name}
                </p>
                <Button onClick={endGame} variant="destructive">End Game</Button>
              </>
            ) : (
              <>
                <p className="mb-4">No game in progress</p>
                <Button onClick={startGame} disabled={queue.length < 4}>Start Game</Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
