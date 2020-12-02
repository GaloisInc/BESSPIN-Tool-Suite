include_directories(
  "${PROJECT_BINARY_DIR}"
  "${PROJECT_SOURCE_DIR}/lib"
  )

link_libraries(CyberphysLib)

# add examples
add_executable(j1939_example j1939_example.c)
add_executable(server server.c)
add_executable(client client.c)
