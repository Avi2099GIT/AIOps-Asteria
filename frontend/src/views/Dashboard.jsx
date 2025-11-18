import React, {useState, useEffect} from 'react'
import PredictForm from '../components/PredictForm'
import RecentList from '../components/RecentList'
import axios from 'axios'
import { motion } from 'framer-motion'

export default function Dashboard(){
  const [recent, setRecent] = useState([])
  const [lastResult, setLastResult] = useState(null)

  const refresh = async ()=>{
    try{
      const resp = await axios.get('/api/anomalies/recent?limit=20')
      setRecent(resp.data)
    }catch(e){
      console.error(e)
    }
  }

  useEffect(()=>{ refresh() }, [])

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2 space-y-4">
        <PredictForm onResult={(r)=>{ setLastResult(r); refresh() }} />
        { lastResult && (
          <motion.div initial={{opacity:0,y:6}} animate={{opacity:1,y:0}} className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Last result</div>
            <pre className="text-xs">{JSON.stringify(lastResult, null, 2)}</pre>
          </motion.div>
        )}
      </div>
      <div className="col-span-1 space-y-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-500 mb-2">Recent anomalies</div>
          <RecentList items={recent} />
          <div className="mt-3 text-right">
            <button onClick={refresh} className="px-3 py-1 text-sm border rounded">Refresh</button>
          </div>
        </div>
      </div>
    </div>
  )
}
