cmake_minimum_required(VERSION 3.8)
project(fishbot_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()

# 安装头文件到指定目录
install(DIRECTORY 
  launch  
  DESTINATION share/${PROJECT_NAME}
)
#以下说明需要注意顺序，否则可能出错
# 加载依赖库：
# - rclcpp：ROS 2 C++ 客户端库
# - geometry_msgs：几何原语的标准消息
# - nav_msgs：ROS 2 的导航消息
# - tf2：ROS 2 的变换库
# - tf2_ros：tf2 库的 ROS 2 集成
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
#设置依赖库到新建的变量dependencies中
set(dependencies
  rclcpp
  geometry_msgs
  nav_msgs
  tf2
  tf2_ros
)
# 指定源文件路径与生成文件名称
add_executable(fishbot_bringup src/fishbot_bringup.cpp)
# 指定源文件路径与生成文件名称,声明语言标准 C 和 C++ 标准为 C99 和 C++17。
target_compile_features(fishbot_bringup PUBLIC c_std_99 cxx_std_17) 
# 将编译目标 'fishbot_bringup' 与所需的依赖项“dependencies”链接。
ament_target_dependencies(fishbot_bringup
  ${dependencies}
)
# 指定头文件查找路径
# 1. **`target_include_directories`**  
#    - 这是一个 CMake 命令，用于为指定的目标（这里是 [`fishbot_bringup`]设置头文件的搜索路径。

# 2. **[`PUBLIC`]
#    - 表示这些包含目录不仅适用于目标本身，还会传播到依赖于该目标的其他目标。这意味着如果其他目标链接了 [`fishbot_bringup`]，它们也会继承这些包含目录。

# 3. **`$<BUILD_INTERFACE:...>`**  
#    - 这是一个生成器表达式，表示在构建阶段使用的包含目录。
#    - `${CMAKE_CURRENT_SOURCE_DIR}/include` 指向当前 CMakeLists.txt 文件所在目录的 [`include`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fzrc%2F%E6%96%87%E6%A1%A3%2FPlatformIO%2FProjects%2Fexample23_mcpwm_control%2Finclude%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%228232262a-f3da-4883-a7a5-7bd778a00a09%22%5D "/home/zrc/文档/PlatformIO/Projects/example23_mcpwm_control/include") 子目录，表示在构建时头文件会从这里查找。

# 4. **`$<INSTALL_INTERFACE:...>`**  
#    - 这是另一个生成器表达式，表示在安装阶段使用的包含目录。
#    - [`include`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fzrc%2F%E6%96%87%E6%A1%A3%2FPlatformIO%2FProjects%2Fexample23_mcpwm_control%2Finclude%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%228232262a-f3da-4883-a7a5-7bd778a00a09%22%5D "/home/zrc/文档/PlatformIO/Projects/example23_mcpwm_control/include") 表示在安装后的头文件路径为 `install_prefix/include`，其中 `install_prefix` 是 CMake 安装的目标路径。
target_include_directories(fishbot_bringup PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
 

# 指定安装文件 'fishbot_bringup' 放到放到那个位置
install(TARGETS fishbot_bringup
  DESTINATION lib/${PROJECT_NAME})




endif()

ament_package()
