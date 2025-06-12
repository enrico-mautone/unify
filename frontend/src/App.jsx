import { Box } from '@chakra-ui/react';
import { renderComponent } from './utils/componentMapper';
import { dashboardLayout } from './data/dashboard';

function App() {
  return (
    <Box minH="100vh" bg="gray.50">
      {renderComponent(dashboardLayout.layout, 'dashboard-root')}
    </Box>
  )
}

export default App
