#pragma once

#include "esphome/core/component.h"

#include <ESPDash.h>
#include <ESPAsyncWebServer.h>


namespace esphome {
namespace dashboard {

class Dashboard : public Component, public ESPDash {
 public:
  Dashboard();

  void setup() override;  // call mark_failed if fails setting up comms
  void dump_config() override;

  void set_port(uint16_t port);

  float get_setup_priority() const {
    // Before WiFi (captive portal)
    return setup_priority::AFTER_WIFI;
  }

  //  void update() override;

 protected:
  AsyncWebServer *server_{nullptr};
  uint16_t port_{80};
};
} // namespace dashboard
} // namespace esphome