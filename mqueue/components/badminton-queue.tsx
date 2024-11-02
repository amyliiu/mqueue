'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function BadmintonQueue() {
  const [queue, setQueue] = useState<string[]>([])
  const [currentPlayers, setCurrentPlayers] = useState<string[]>([])
  const [playerName, setPlayerName] = useState('')

  const addToQueue = (e: React.FormEvent) => {
    e.preventDefault()
    if (playerName.trim()) {
      setQueue([...queue, playerName.trim()])
      setPlayerName('')
    }
  }

  const startGame = () => {
    if (queue.length >= 4) {
      const newPlayers = queue.slice(0, 4)
      setCurrentPlayers(newPlayers)
      setQueue(queue.slice(4))
    }
  }

  const endGame = () => {
    setCurrentPlayers([])
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Badminton Queue</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Add Player to Queue</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={addToQueue} className="flex space-x-2">
            <Input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter player name"
              className="flex-grow"
            />
            <Button type="submit">Add to Queue</Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Current Queue</CardTitle>
          </CardHeader>
          <CardContent>
            {queue.length > 0 ? (
              <ol className="list-decimal list-inside">
                {queue.map((player, index) => (
                  <li key={index} className="mb-1">{player}</li>
                ))}
              </ol>
            ) : (
              <p>No players in queue</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Current Game</CardTitle>
          </CardHeader>
          <CardContent>
            {currentPlayers.length === 4 ? (
              <>
                <p className="mb-4">
                  Team 1: {currentPlayers[0]} & {currentPlayers[1]}
                  <br />
                  Team 2: {currentPlayers[2]} & {currentPlayers[3]}
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