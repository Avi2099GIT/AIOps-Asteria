import React from 'react'
import AnomalyCard from './AnomalyCard'

export default function RecentList({items}){
  if(!items || items.length===0) return <div className="text-sm text-gray-500">No recent anomalies</div>
  return (
    <div className="grid grid-cols-1 gap-3">
      {items.map((it, idx)=> <AnomalyCard key={idx} item={it} />)}
    </div>
  )
}
