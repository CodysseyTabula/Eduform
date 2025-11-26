import React, { useState } from 'react';
import './Sidebar.css';

interface SidebarProps {
  title: string;
  menuItems: string[];
  onMenuItemClick?: (item: string) => void;
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  title, 
  menuItems, 
  onMenuItemClick,
  className 
}) => {
  const [activeItem, setActiveItem] = useState<string | null>(null);

  const handleClick = (item: string) => {
    setActiveItem(item);
    if (onMenuItemClick) {
      onMenuItemClick(item);
    }
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

