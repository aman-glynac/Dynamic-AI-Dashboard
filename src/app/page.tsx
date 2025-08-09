import Canvas from '@/components/Canvas'
import PromptInput from '@/components/PromptInput'

export default function Home() {
  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1">
        <Canvas />
      </div>
      <div className="border-t border-gray-200">
        <PromptInput />
      </div>
    </div>
  )
}