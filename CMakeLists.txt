cmake_minimum_required(VERSION 2.8.9)

project(GyroGuide)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Modules/GyroGuide")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "Ruifeng Chen, Luping Fang, Qing Pan (College of Information Engineering, Zhejiang University of Technology, Hangzhou, China),Xiaolei Chen, Jiashu Zhang (Department of Neurosurgery, PLA General Hospital, Beijing, China)")
set(EXTENSION_DESCRIPTION "An python extension of 3D Slicer helps surgeons implement puncture orientation.")
set(EXTENSION_ICONURL "http://www.slicer.org/slicerWiki/images/a/a7/GyroGuide.png")
set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/index.php/File:GyroGuide-Step-2.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
add_subdirectory(GyroGuide)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
