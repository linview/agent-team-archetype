// Example Service - 后端工程架构范例入口
//
// 配置文件加载机制：
//  1. 优先使用 -f 参数指定的配置文件
//  2. 未指定 -f 时，从环境变量 CONFIG_FILE 读取
//  3. 环境变量未设置时，使用默认值 etc/config/config.yaml
//
// K8s 部署配置路径：/app/etc/config/config-<environment>.yaml
//
// 说明：这是一个最小可运行骨架——加载配置并启动 HTTP 服务器。
// 实际业务 handler 注册在 internal/handler，ServiceContext 在 internal/svc；
// 范例中这两层留空（仅 .gitkeep），作为分层架构的占位，重点展示数据层
// （internal/model + internal/dao）与服务组装方式。
package main

import (
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"example-service/internal/config"

	"github.com/zeromicro/go-zero/core/conf"
	"github.com/zeromicro/go-zero/rest"
)

var configFile = flag.String("f", "", "the config file")

func main() {
	flag.Parse()

	// 如果未指定 -f 参数，从环境变量读取
	configPath := *configFile
	if configPath == "" {
		if configPath = os.Getenv("CONFIG_FILE"); configPath == "" {
			configPath = "etc/config/config.yaml" // 默认值
		}
	}

	var c config.Config
	conf.MustLoad(configPath, &c)

	server := rest.MustNewServer(c.RestConf, rest.WithUnauthorizedCallback(func(w http.ResponseWriter, r *http.Request, err error) {
		http.Error(w, err.Error(), http.StatusUnauthorized)
	}))

	// 范例：业务 handler 与 ServiceContext 在此装配
	//   svcContext := svc.NewServiceContext(c)
	//   handler.RegisterHandlers(server, svcContext)
	// 本范例仅展示服务骨架，实际业务层留空。

	fmt.Printf("Starting example-service at %s:%d...\n", c.RestConf.Host, c.RestConf.Port)

	// Start server in a goroutine for graceful shutdown
	go func() {
		server.Start()
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	fmt.Println("\nShutting down server...")
	server.Stop()
	fmt.Println("Server stopped gracefully")
}
