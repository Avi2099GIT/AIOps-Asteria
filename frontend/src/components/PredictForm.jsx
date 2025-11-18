import React, {useState} from 'react'
import axios from 'axios'
import { motion } from 'framer-motion'

export default function PredictForm({onResult}){
  const [message, setMessage] = useState('Error: timeout talking to payment provider')
  const [service, setService] = useState('checkout-service')
  const [environment, setEnvironment] = useState('prod')
  const [loading, setLoading] = useState(false)

  const submit = async ()=>{
    setLoading(true)
    try{
      const resp = await axios.post('/api/predict/anomaly', {
        tenant_id: 'demo-tenant',
        service,
        environment,
        message
      })
      onResult(resp.data)
    }catch(e){
      console.error(e)
      alert('Prediction failed: ' + (e?.response?.data?.detail || e.message))
    }finally{ setLoading(false) }
  }

  return (
    <motion.div initial={{opacity:0}} animate={{opacity:1}} className="bg-white rounded-lg shadow p-4 space-y-3">
      <div className="text-sm text-gray-500">Quick anomaly scoring</div>
      <input value={service} onChange={e=>setService(e.target.value)} className="w-full border p-2 rounded"/>
      <input value={environment} onChange={e=>setEnvironment(e.target.value)} className="w-full border p-2 rounded"/>
      <textarea value={message} onChange={e=>setMessage(e.target.value)} className="w-full border p-2 rounded" rows={4}/>
      <div className="flex gap-2">
        <button onClick={submit} className="px-4 py-2 bg-indigo-600 text-white rounded disabled:opacity-60" disabled={loading}>
          {loading? 'Scoring...' : 'Score anomaly'}
        </button>
        <button onClick={()=>{ setMessage('') }} className="px-4 py-2 border rounded">Clear</button>
      </div>
    </motion.div>
  )
}
