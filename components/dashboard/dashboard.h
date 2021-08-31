#pragma once

#include "esphome/core/component.h"
#include "esphome/components/web_server_base/web_server_base.h"

#include <ESPDash.h>
#include <ESPAsyncWebServer.h>


namespace esphome {
namespace dashboard {

class Dashboard : public Component, public ESPDash {
 public:
  Dashboard(web_server_base::WebServerBase *base);

  void setup() override;  // call mark_failed if fails setting up comms
  void dump_config() override;

  float get_setup_priority() const {
    return setup_priority::AFTER_WIFI;
  }

 protected:
  web_server_base::WebServerBase *base_;
  uint16_t port_{80};
};
} // namespace dashboard
} // namespace esphome