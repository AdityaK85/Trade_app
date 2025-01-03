import { log, emailValidator,filedValidator, callAjax, fieldsValidator, removeError, resetControls,sweetAlertMsg, showToastMsg } from '../CommonJS/common.js';

window.removeError = removeError

class CustomDatafeed {
    onReady(callback) {
      setTimeout(() => callback({ supports_marks: false, supports_timescale_marks: false, supports_time: true }), 0);
    }
  
    resolveSymbol(symbolName, onResolve, onError) {
      setTimeout(() => {
        onResolve({
          ticker: symbolName,
          name: symbolName,
          session: "24x7",
          timezone: "Etc/UTC",
          minmov: 1,
          pricescale: 100,
          has_intraday: true,
          has_no_volume: false,
          supported_resolutions: ["1D", "1W", "1M"],
        });
      }, 0);
    }
  
    getBars(symbolInfo, resolution, from, to, onHistoryCallback, onErrorCallback) {
      const bars = [
        { time: 1687225200000, open: 100, high: 110, low: 95, close: 105, volume: 1000 },
        { time: 1687311600000, open: 105, high: 115, low: 102, close: 110, volume: 1200 },
      ];
      onHistoryCallback(bars, { noData: false });
    }
  
    subscribeBars(symbolInfo, resolution, onRealtimeCallback, subscribeUID, onResetCacheNeededCallback) {
      setInterval(() => {
        const lastBar = { time: Date.now(), open: 110, high: 120, low: 108, close: 115, volume: 1500 };
        onRealtimeCallback(lastBar);
      }, 1000);
    }
  
    unsubscribeBars(subscriberUID) {}
  }
  
  var datafeed = new CustomDatafeed();

function delay(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }
  
  function initOnReady() {
    // class CustomDatafeed extends Datafeeds.UDFCompatibleDatafeed {}
  
    // var datafeed = new CustomDatafeed(
    //   "https://demo-feed-data.tradingview.com",
    //   undefined,
    //   {
    //     maxResponseLength: 1000,
    //     expectedOrder: "latestFirst"
    //   }
    // );
  
    class CustomBroker extends Brokers.BrokerSample {
      constructor(host, quotesProvider) {
        super(host, quotesProvider);
        this.customPnL = this._host.factory.createWatchedValue(123456);
        // This will simulate some P&L updates (once a second)
        setInterval(() => {
          const randomDelta = Math.random() * 10;
          this.myCustomUpdate(randomDelta);
        }, 1000);
      }
  
      accountManagerInfo() {
        const result = super.accountManagerInfo();
        result.customFormatters = [
          {
            name: "custom-type",
            formatText: (dataFields) => {
              return dataFields.values[0];
            }
          },
          {
            name: "custom-button",
            formatElement: (dataFields) => {
              const price = dataFields.values[0];
              const button = document.createElement("button");
  
              button.innerText = "Alert";
  
              button.addEventListener("click", () => {
                event.stopPropagation();
                this._host.showNotification(
                  "The button is clicked",
                  `The price is: ${price}`,
                  1
                );
              });
  
              return button;
            }
          }
        ];
        result.positionColumns.splice(2, 0, {
          label: "Custom",
          help: "Custom Column",
          id: "custom",
          formatter: "custom-type",
          alignment: "left",
          dataFields: ["custom"]
        });
        result.positionColumns.splice(3, 0, {
          label: "Button",
          help: "Custom Button",
          id: "custom-button",
          formatter: "custom-button",
          alignment: "left",
          dataFields: ["avgPrice"]
        });
  
        const summaryProps = [
          {
            text: "My Custom P&L",
            wValue: this.customPnL,
            formatter: "fixed"
          }
        ];
        result.summary = summaryProps;
  
        return result;
      }
  
      positions() {
        return new Promise(async (resolve) => {
          resolve([
            {
              avgPrice: 173.68,
              id: "test-position",
              openTimeInMs: 1687162188000,
              pl: -12.34,
              qty: 20,
              side: 1,
              stopLoss: 141.55,
              swap: 0,
              takeProfit: 142.15,
              symbol: "NasdaqNM:AAPL",
              custom: 43.21
            }
          ]);
        });
      }
  
      myCustomUpdate(delta) {
        this._host.positionUpdate({
          avgPrice: 173.68,
          id: "test-position",
          openTimeInMs: 1687162188000,
          pl: -12.34 + delta,
          qty: 20,
          side: 1,
          stopLoss: 141.55,
          swap: 0,
          takeProfit: 142.15,
          symbol: "NasdaqNM:AAPL",
          custom: (43.21 + delta).toFixed(2)
        });
        this.customPnL.setValue(123456 + delta * 10);
      }
    }
  
    var widget = (window.tvWidget = new TradingView.widget({
      library_path:
        "https://trading-terminal.tradingview-widget.com/charting_library/",
      // debug: true, // uncomment this line to see Library errors and warnings in the console
      fullscreen: true,
      symbol: "AAPL",
      interval: "1D",
      container: "tv_chart_container",
      datafeed: datafeed,
      locale: "en",
      disabled_features: ["show_right_widgets_panel_by_default"],
  
      broker_factory: function (host) {
        window.tradingHost = host;
        return new CustomBroker(host, datafeed);
      },
      broker_config: {
        configFlags: {
          supportClosePosition: true,
          supportPLUpdate: true,
          supportEditAmount: false,
          supportModifyOrderPrice: true,
          supportModifyBrackets: true,
          supportOrderBrackets: true,
          supportPositionBrackets: true,
          calculatePLUsingLast: true
        }
      }
    }));
  }
  
  window.addEventListener("DOMContentLoaded", initOnReady, false);


window.handleLiveData = function (live_data_web) {
    // const live_data = JSON.parse(live_data_web['live_data']);
    // const classToElementsMap = {};
    // Object.keys(live_data).forEach(token => {
    //     const classes = [`nfty_${token}_ltp`, `bnf_${token}_ltp`];
    //     classes.forEach(td_class => {
    //         if (!classToElementsMap[td_class]) {
    //             classToElementsMap[td_class] = Array.from(document.getElementsByClassName(td_class));
    //         }
    //     });
    // });
    // Object.keys(live_data).forEach(token => {
    //     const ltpValue = live_data[token].ltp;
    //     const classes = [`nfty_${token}_ltp`, `bnf_${token}_ltp` , `equity_${token}_ltp`];
    //     classes.forEach(td_class => {
    //         const elements = classToElementsMap[td_class] || [];
    //         elements.forEach(element => {
    //             element.innerHTML = ltpValue;
    //         });
    //     });
    // });
    // updateLiveLtp_ForStrikePrice($("#indexSelect").val() , live_data)
}
