# Setup Notes

## macOS M3 Build Fixes

### Issue: OpticalFlow plugin build failure
**File:** `PX4-Autopilot/src/modules/simulation/gz_plugins/CMakeLists.txt`

**Changes made:**
1. Commented out: `# add_subdirectory(optical_flow)`
2. Removed `OpticalFlowSystem` from both `add_custom_target` lines

**Reason:** Library extension mismatch (.so vs .dylib) on macOS
**Impact:** None - optical flow sensor not needed for GPS navigation
**Date:** 2026-01-20

### Other fixes applied:
- Changed `-Wdouble-promotion` to `-Wno-double-promotion` in `cmake/px4_add_common_flags.cmake`
- See main README for details
