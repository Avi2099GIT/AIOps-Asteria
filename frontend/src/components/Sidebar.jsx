import React from 'react'
export default function Sidebar(){
  return (
    <aside className="w-72 bg-gradient-to-b from-white to-gray-50 border-r min-h-screen p-6">
      <div className="mb-8">
        <div className="text-xs uppercase text-gray-400">Workspace</div>
        <div className="mt-2 font-medium">Demo Tenant</div>
      </div>

      <nav className="space-y-2">
        <a className="block px-3 py-2 rounded-md bg-indigo-50 text-indigo-700">Dashboard</a>
        <a className="block px-3 py-2 rounded-md hover:bg-gray-100">Incidents</a>
        <a className="block px-3 py-2 rounded-md hover:bg-gray-100">Playbooks</a>
        <a className="block px-3 py-2 rounded-md hover:bg-gray-100">Settings</a>
      </nav>

      <div className="mt-8 text-sm text-gray-500">
        Version: <strong>0.1.0</strong>
      </div>
    </aside>
  )
}
