import { useState } from 'react'
import './App.css'
import { 
  Header, 
  Sidebar, 
  NameCard, 
  TextBox, 
  Dropdown, 
  CheckboxGroup, 
  Button, 
  TabButton,
  Line
} from './components'

function App() {
  const [selectedTab, setSelectedTab] = useState('tab1')

  return (
    <div className="app">
      <Header />
      
      <div className="app-layout">
        <Sidebar
          title="메뉴"
          menuItems={['홈', '설정', '도움말', '정보']}
          onMenuItemClick={(item) => console.log('선택된 메뉴:', item)}
        />
        
        <main className="app-main">
          <div className="component-section">
            <h2>컴포넌트 미리보기</h2>
            
            <div className="component-group">
              <h3>NameCard</h3>
              <NameCard
                title="이름 카드"
                description="이것은 NameCard 컴포넌트입니다."
              />
            </div>

            <div className="component-group">
              <h3>TextBox</h3>
              <TextBox>
                <p>이것은 TextBox 컴포넌트입니다.</p>
              </TextBox>
            </div>

            <div className="component-group">
              <h3>Dropdown</h3>
              <Dropdown
                options={['옵션 1', '옵션 2', '옵션 3', '옵션 4']}
                placeholder="선택하세요"
                onSelect={(option) => console.log('선택된 옵션:', option)}
              />
            </div>

            <div className="component-group">
              <h3>CheckboxGroup</h3>
              <CheckboxGroup
                options={[
                  { id: '1', label: '체크박스 1' },
                  { id: '2', label: '체크박스 2' },
                  { id: '3', label: '체크박스 3' }
                ]}
                onSelectionChange={(selectedIds) => console.log('선택된 항목:', selectedIds)}
              />
            </div>

            <div className="component-group">
              <h3>Button</h3>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <Button arrowDirection="left">이전</Button>
                <Button arrowDirection="right">다음</Button>
                <Button>버튼</Button>
              </div>
            </div>

            <div className="component-group">
              <h3>TabButton</h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <TabButton 
                  isSelected={selectedTab === 'tab1'}
                  onClick={() => setSelectedTab('tab1')}
                >
                  탭 1
                </TabButton>
                <TabButton 
                  isSelected={selectedTab === 'tab2'}
                  onClick={() => setSelectedTab('tab2')}
                >
                  탭 2
                </TabButton>
              </div>
            </div>

            <div className="component-group">
              <h3>Line</h3>
              <Line />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
