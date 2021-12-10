#pragma once

#include "esphome/core/component.h"
#include "esphome/components/web_server_base/web_server_base.h"

#include <ESPDash.h>
#include <ESPAsyncWebServer.h>


namespace esphome {
namespace dashboard {

class Dashboard : public Component, public ESPDash {
 public:
  Dashboard(std::shared_ptr<web_server_base::WebServerBase> base);
  ~Dashboard();

  void setup() override;  // call mark_failed if fails setting up comms
  void dump_config() override;

  float get_setup_priority() const {
    return setup_priority::AFTER_WIFI;
  }

 protected:
  std::shared_ptr<web_server_base::WebServerBase> base_{ nullptr };
  uint16_t port_{80};
};
} // namespace dashboard
} // namespace esphome