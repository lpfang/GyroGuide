cmake_minimum_required(VERSION 2.8.9)

project(GyroGuide)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "https://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/GyroGuide")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "Ruifeng Chen, Luping Fang, Qing Pan (College of Information Engineering, Zhejiang University of Technology, Hangzhou, China),Xiaolei Chen, Jiashu Zhang (Department of Neurosurgery, PLA General Hospital, Beijing, China)")
set(EXTENSION_DESCRIPTION "GyroGuide determines the trajectory angle and depth of puncture path, and transmits the calculated information to the probe for real time navigation.")
set(EXTENSION_ICONURL "https://www.slicer.org/slicerWiki/images/a/a7/GyroGuide.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/slicerWiki/images/8/80/GyroGuide-Step-2.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
add_subdirectory(GyroGuide)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
