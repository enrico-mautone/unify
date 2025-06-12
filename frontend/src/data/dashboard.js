

export const dashboardLayout = {
  layout: {
    type: "box",
    props: {
      display: "flex",
      minH: "100vh",
      bg: "gray.50"
    },
    children: [
      // Sidebar
      {
        type: "box",
        props: {
          w: "64",
          bg: "white",
          borderRight: "1px",
          borderColor: "gray.200",
          p: 4,
          display: "flex",
          flexDirection: "column"
        },
        children: [
          // Logo
          {
            type: "box",
            props: {
              p: 3,
              mb: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between"
            },
            children: [
              {
                type: "heading",
                props: {
                  size: "lg",
                  color: "blue.500"
                },
                content: "Unify"
              },
              {
                type: "iconbutton",
                props: {
                  icon: {
                    type: "icon",
                    component: "ChevronDownIcon"
                  },
                  size: "sm",
                  variant: "ghost",
                  'aria-label': "Menu"
                }
              }
            ]
          },
          // Navigation
          {
            type: "vstack",
            props: {
              spacing: 1,
              flex: 1,
              align: "stretch"
            },
            children: [
              // Dashboard button with active state
              {
                type: "button",
                props: {
                  variant: "ghost",
                  justifyContent: "flex-start",
                  leftIcon: {
                    type: "icon",
                    component: "CalendarIcon",
                    props: { boxSize: 5 }
                  },
                  colorScheme: "blue",
                  bg: "blue.50",
                  color: "blue.700",
                  _hover: { bg: "blue.100" },
                  _active: { bg: "blue.100" },
                  py: 2,
                  px: 3,
                  borderRadius: "md"
                },
                content: "Dashboard"
              },
              // Other navigation items
              ["Activity", "Messages"].map((item, index) => ({
                type: "button",
                props: {
                  key: index,
                  variant: "ghost",
                  justifyContent: "flex-start",
                  leftIcon: {
                    type: "icon",
                    component: `${item === 'Activity' ? 'TimeIcon' : 'ChatIcon'}`,
                    props: { boxSize: 5 }
                  },
                  color: "gray.600",
                  _hover: { bg: "gray.100" },
                  _active: { bg: "gray.100" },
                  py: 2,
                  px: 3,
                  borderRadius: "md"
                },
                content: item
              })),
              // Settings at the bottom
              {
                type: "button",
                props: {
                  variant: "ghost",
                  justifyContent: "flex-start",
                  leftIcon: {
                    type: "icon",
                    component: "SettingsIcon",
                    props: { boxSize: 5 }
                  },
                  color: "gray.600",
                  _hover: { bg: "gray.100" },
                  _active: { bg: "gray.100" },
                  py: 2,
                  px: 3,
                  borderRadius: "md",
                  mt: "auto"
                },
                content: "Settings"
              }
            ]
          }
        ]
      },
      // Main content
      {
        type: "box",
        props: {
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden"
        },
        children: [
          // Header
          {
            type: "box",
            props: {
              bg: "white",
              borderBottom: "1px",
              borderColor: "gray.200",
              p: 4,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between"
            },
            children: [
              // Left side - Search bar
              {
                type: "box",
                props: {
                  maxW: "md",
                  flex: 1,
                  position: "relative"
                },
                children: [
                  {
                    type: "input",
                    props: {
                      type: "text",
                      placeholder: "Search...",
                      pl: 10,
                      pr: 4,
                      py: 2,
                      w: "100%",
                      rounded: "lg",
                      border: "1px",
                      borderColor: "gray.200",
                      _focus: {
                        borderColor: "blue.500",
                        boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)"
                      }
                    }
                  },
                  {
                    type: "box",
                    props: {
                      position: "absolute",
                      left: 3,
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "gray.400"
                    },
                    children: [
                      {
                        type: "icon",
                        component: "SearchIcon"
                      }
                    ]
                  }
                ]
              },
              // Right side - Icons and user
              {
                type: "hstack",
                props: {
                  spacing: 4,
                  ml: 4
                },
                children: [
                  {
                    type: "iconbutton",
                    props: {
                      icon: {
                        type: "icon",
                        component: "BellIcon"
                      },
                      variant: "ghost",
                      color: "gray.600",
                      'aria-label': "Notifications",
                      borderRadius: "full"
                    }
                  },
                  {
                    type: "hstack",
                    props: {
                      spacing: 2,
                      alignItems: "center",
                      cursor: "pointer",
                      _hover: { bg: "gray.100" },
                      p: 1,
                      pr: 3,
                      rounded: "full"
                    },
                    children: [
                      {
                        type: "avatar",
                        props: {
                          size: "sm",
                          name: "John Doe",
                          cursor: "pointer"
                        }
                      },
                      {
                        type: "text",
                        props: {
                          fontWeight: "medium",
                          color: "gray.700"
                        },
                        content: "John Doe"
                      }
                    ]
                  }
                ]
              }
            ]
          },
          // Page content (empty for now)
          {
            type: "box",
            props: {
              flex: 1,
              p: 6,
              overflow: "auto"
            },
            children: []
          }
        ]
      }
    ]
  }
};

export default dashboardLayout;
