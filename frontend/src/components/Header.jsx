import React from 'react'
export default function Header(){
  return (
    <header className="bg-white shadow-sm py-4 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-semibold">Asteria AIOps</h1>
        <span className="text-sm text-gray-500">Operational Intelligence</span>
      </div>
      <div className="flex items-center gap-4">
        <button className="px-3 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700">New Alert</button>
        <div className="text-sm text-gray-600">demo-tenant</div>
      </div>
    </header>
  )
}
