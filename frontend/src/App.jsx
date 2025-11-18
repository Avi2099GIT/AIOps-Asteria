import React from 'react'
import Dashboard from './views/Dashboard'
import Header from './components/Header'
import Sidebar from './components/Sidebar'

export default function App(){
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="p-6">
          <Dashboard />
        </main>
      </div>
    </div>
  )
}
