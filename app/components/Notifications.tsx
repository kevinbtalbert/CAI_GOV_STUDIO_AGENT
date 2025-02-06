import { notification } from 'antd';
import { ReactNode, createContext, useContext } from 'react';

const NotificationContext = createContext<any>(null);

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  const [api, contextHolder] = notification.useNotification();

  return (
    <NotificationContext.Provider value={api}>
      {contextHolder}
      {children}
    </NotificationContext.Provider>
  );
};

export const useGlobalNotification = () => useContext(NotificationContext);
