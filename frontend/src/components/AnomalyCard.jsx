import React from 'react'
import { motion } from 'framer-motion'

export default function AnomalyCard({item}){
  return (
    <motion.div initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} className="bg-white rounded-lg shadow p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-gray-500">{item.service} · {item.environment}</div>
          <div className="text-lg font-semibold">{item.anomaly_score.toFixed(3)}</div>
          <div className="text-xs text-gray-600 mt-1">Severity: <strong>{item.severity}</strong></div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">{new Date(item.created_at).toLocaleString()}</div>
        </div>
      </div>
    </motion.div>
  )
}
