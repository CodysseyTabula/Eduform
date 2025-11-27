import React, { useState, useEffect } from 'react';
import './Sidebar.css';

interface SidebarProps {
  title: string;
  menuItems: string[];
  onMenuItemClick?: (item: string) => void;
  activeItem?: string | null;
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  title, 
  menuItems, 
  onMenuItemClick,
  activeItem: externalActiveItem,
  className 
}) => {
  const [internalActiveItem, setInternalActiveItem] = useState<string | null>(null);
  
  // 외부에서 activeItem이 제공되면 사용하고, 아니면 내부 상태 사용
  const activeItem = externalActiveItem !== undefined ? externalActiveItem : internalActiveItem;

  useEffect(() => {
    // 외부 activeItem이 변경되면 내부 상태도 업데이트
    if (externalActiveItem !== undefined) {
      setInternalActiveItem(externalActiveItem);
    }
  }, [externalActiveItem]);

  const handleClick = (item: string) => {
    // 외부에서 activeItem이 제공되지 않을 때만 내부 상태 업데이트
    if (externalActiveItem === undefined) {
      setInternalActiveItem(item);
    }
    onMenuItemClick?.(item);
  };

  return (
    <aside className={`sidebar ${className || ''}`}>
      <h2 className="sidebar-title">{title}</h2>
      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          {menuItems.map((item, index) => (
            <li key={index}>
              <button
                className={`sidebar-menu-item ${
                  activeItem === item ? 'active' : ''
                }`}
                onClick={() => handleClick(item)}
              >
                {item}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;

