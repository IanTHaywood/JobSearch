import { useState } from 'react'
import './App.css'
import { ApiControlTab } from './components/ApiControlTab'
import { DataTab } from './components/DataTab'

type Tab = 'data' | 'api-control'

function App() {
  const [tab, setTab] = useState<Tab>('data')

  return (
    <div className="app">
      <header>
        <h1>JobSearch Control</h1>
        <nav className="tabs">
          <button
            className={tab === 'data' ? 'active' : ''}
            onClick={() => setTab('data')}
          >
            Data
          </button>
          <button
            className={tab === 'api-control' ? 'active' : ''}
            onClick={() => setTab('api-control')}
          >
            API Control
          </button>
        </nav>
      </header>
      <main>{tab === 'data' ? <DataTab /> : <ApiControlTab />}</main>
    </div>
  )
}

export default App
