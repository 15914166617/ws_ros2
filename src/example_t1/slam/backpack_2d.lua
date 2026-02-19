-- Copyright 2016 The Cartographer Authors
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- 包含地图构建器和轨迹构建器的Lua文件
include "map_builder.lua"
include "trajectory_builder.lua"

-- 了解自己需要提供那些数据,不同的设置分别对应了什么？
-- 配置选项表格（对比小鱼，和chatgpt,学习设置） base_link imu_Link base_footprint
options = {
  map_builder = MAP_BUILDER,                        -- 地图构建器。可以是一个变量名，指向地图构建器的实例或对象。
  trajectory_builder = TRAJECTORY_BUILDER,          -- 轨迹构建器。可以是一个变量名，指向轨迹构建器的实例或对象。
  map_frame = "map",                                -- 地图坐标系。这是地图在ROS中的坐标系名称。
  tracking_frame = "base_link",                     -- 跟踪坐标系。这是用于跟踪的坐标系，在ROS中通常是机器人的底盘或基准坐标系。
  published_frame = "base_link",
--   published_frame = "scan_Link",
--   published_frame = "odom",
  odom_frame = "odom",                              -- 里程计坐标系。这是里程计数据所使用的坐标系，在ROS中通常是机器人的里程计坐标系。
  
  provide_odom_frame = true,                       -- 是否提供里程计坐标系。设置为true表示提供里程计坐标系，设置为false则不提供。
  publish_frame_projected_to_2d = false,            -- 是否发布投影到2D的坐标系。设置为true表示发布2D投影坐标系，设置为false则不进行投影。
  use_pose_extrapolator = false,                     -- 是否使用姿态外推器
  use_odometry = true,                             -- 是否使用里程计数据。设置为true表示使用里程计数据，设置为false则不使用。
  use_nav_sat = false,                              -- 是否使用导航卫星数据。设置为true表示使用导航卫星数据，设置为false则不使用。
  use_landmarks = false,                            -- 是否使用地标数据。设置为true表示使用地标数据，设置为false则不使用。
--   use_landmarks = true,
--   provide_odom_frame = false,
--   publish_frame_projected_to_2d = true,
--   use_odometry = true,
--   use_nav_sat = false,
--   use_landmarks = false,

  num_laser_scans = 1,                              -- 激光雷达的数量(单回波激光传感器)
  num_multi_echo_laser_scans = 0,                   -- 激光雷达的数量(多回波激光传感器)
  num_subdivisions_per_laser_scan = 1,             -- 每个激光扫描的细分数(调大了会导致建图只有一部分？不知道玩什么)
--   num_subdivisions_per_laser_scan = 2,             -- 每个激光扫描的细分数(调大了会导致建图只有一部分？不知道玩什么)
  num_point_clouds = 0,                             -- 点云数据的数量(3D精准有关)
--   lookup_transform_timeout_sec = 0.2,               -- 查找坐标变换的超时时间
  lookup_transform_timeout_sec = 0.1,

--   submap_publish_period_sec = 0.3,                  -- 发布子地图的时间间隔
--   pose_publish_period_sec = 5e-3,                   -- 发布姿态的时间间隔
--   trajectory_publish_period_sec = 30e-3,    

  submap_publish_period_sec = 0.0333,                  -- 发布子地图的时间间隔
  pose_publish_period_sec = 0.0333,                   -- 发布姿态的时间间隔 
  trajectory_publish_period_sec = 0.0333,            -- 发布轨迹的时间间隔

  rangefinder_sampling_ratio = 1.,                  -- 激光测距仪的采样率
  odometry_sampling_ratio = 1.,                     -- 里程计的采样率
  fixed_frame_pose_sampling_ratio = 1.,             -- 固定坐标系的姿态采样率 ,不是1时会导致建图时出错，但是改成30可以自我定位更准确
  imu_sampling_ratio = 1.,                          -- IMU数据的采样率 基本1.0
  landmarks_sampling_ratio = 1.,                    -- 地标数据的采样率

--   rangefinder_sampling_ratio = 1.,                  -- 激光测距仪的采样率
--   odometry_sampling_ratio = 1.,                     -- 里程计的采样率
--   fixed_frame_pose_sampling_ratio = 0.5,             -- 固定坐标系的姿态采样率 ,不是1时会导致建图时出错，但是改成30可以自我定位更准确
--   imu_sampling_ratio = 1.,                          -- IMU数据的采样率 基本1.0
--   landmarks_sampling_ratio = 1.,                    -- 地标数据的采样率
}

-- 使用2D轨迹构建器
MAP_BUILDER.use_trajectory_builder_2d = true
-- 设置累积的激光数据数量为10
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 10


-- 这些参数很重要，因为目前不加会有建图只有左上角有图，加了后范围缩短了，但是建图是环绕了
-- 0改成0.10,比机器人半径小的都忽略
TRAJECTORY_BUILDER_2D.min_range = 0.1
-- 30改成3.5,限制在雷达最大扫描范围内，越小一般越精确些
TRAJECTORY_BUILDER_2D.max_range = 3.0
-- 5改成3,传感器数据超出有效范围最大值
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 5.


-- 返回配置选项
return options
