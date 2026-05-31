ALPHA_BUILD_BRANCH := alpha-16.2
ALPHA_BUILD_VERSION := 4.5
ALPHA_MAINTAINER ?= buildbot

ifeq ($(ALPHA_VERSION_APPEND_TIME_OF_DAY),true)
    ALPHA_BUILD_DATE := $(shell date -u +%Y%m%d_%H%M%S)
else
    ALPHA_BUILD_DATE := $(shell date -u +%Y%m%d)
endif

ifeq ($(strip $(ALPHA_BUILD_TYPE)),)
  ALPHA_RELEASE_TYPE := Unofficial
  else
    ifeq ($(filter-out OFFICIAL Official official, $(strip $(ALPHA_BUILD_TYPE))),)
      ALPHA_RELEASE_TYPE := Official
    else
      ALPHA_RELEASE_TYPE := Unofficial
  endif
endif

# TARGET_BUILD_PACKAGE options:
# 1 - vanilla (default)
# 2 - microg
# 3 - gapps
TARGET_BUILD_PACKAGE ?= 1
ifeq ($(TARGET_BUILD_PACKAGE),3)
  ALPHA_BUILD_VARIANT := gapps
else
  ifeq ($(TARGET_BUILD_PACKAGE),2)
    ALPHA_BUILD_VARIANT := microg
  else
    ALPHA_BUILD_VARIANT := vanilla
  endif
endif

ALPHA_DEVICE := $(ALPHA_BUILD)

# Internal version
ALPHA_VERSION := $(PLATFORM_VERSION)-$(ALPHA_BUILD_DATE)-$(ALPHA_BUILD_VARIANT)-$(ALPHA_DEVICE)-v$(ALPHA_BUILD_VERSION)

# Display version
ALPHA_DISPLAY_VERSION := AlphaDroid-$(ALPHA_BUILD_VERSION)-$(ALPHA_BUILD_VARIANT)-$(ALPHA_DEVICE)

PRODUCT_SYSTEM_EXT_PROPERTIES += \
    ro.alpha.version=$(ALPHA_VERSION) \
    ro.alpha.release.type=$(ALPHA_RELEASE_TYPE) \
    ro.alpha.build.branch=$(ALPHA_BUILD_BRANCH) \
    ro.alpha.build.version=$(ALPHA_BUILD_VERSION) \
    ro.alpha.build.variant=$(ALPHA_BUILD_VARIANT) \
    ro.alpha.build.date=$(ALPHA_BUILD_DATE) \
    ro.alpha.device=$(ALPHA_DEVICE) \
    ro.alpha.maintainer=$(ALPHA_MAINTAINER)
