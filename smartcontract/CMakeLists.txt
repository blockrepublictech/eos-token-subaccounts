cmake_minimum_required( VERSION 3.5 )
project ( "Test-App" VERSION 1.0 LANGUAGES NONE
)

include( CTest )

add_custom_target( wast ALL COMMAND python3 -m eosfactory.build \"${CMAKE_SOURCE_DIR}\" --c_cpp_prop \"${CMAKE_SOURCE_DIR}/.vscode/c_cpp_properties.json\" )
