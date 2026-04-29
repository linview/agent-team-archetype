// Resource Meter - Kubernetes {BUSINESS_DESCRIPTION}平台
//
// 配置文件加载机制：
//  1. 优先使用 -f 参数指定的配置文件
//  2. 未指定 -f 时，从环境变量 CONFIG_FILE 读取
//  3. 环境变量未设置时，使用默认值 etc/config/config.yaml
//
// K8s 部署配置路径：/app/etc/config/config-<environment>.yaml
package main

import (
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"{PROJECT_NAME}/internal/config"
	"{PROJECT_NAME}/internal/handler"
	"{PROJECT_NAME}/internal/svc"

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

	svcContext := svc.NewServiceContext(c)
	defer svcContext.Close() // Graceful shutdown: close DB pool, stop Informer

	handler.RegisterHandlers(server, svcContext)

	fmt.Printf("Starting GPU Usage Stats API at %s:%d...\n", c.RestConf.Host, c.RestConf.Port)

	// ✅ NEW: Start Informer and Worker
	ctx := context.Background()
	if err := svcContext.Start(ctx); err != nil {
		fmt.Printf("Failed to start Informer: %v\n", err)
		panic(err)
	}

	// Start server in a goroutine for graceful shutdown
	fmt.Println("Starting HTTP server in goroutine...")
	go func() {
		fmt.Println("HTTP server Start() called, beginning to listen...")
		server.Start()
		fmt.Println("HTTP server stopped")
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	fmt.Println("\nShutting down server...")

	// Gracefully shutdown the server
	server.Stop()

	fmt.Println("Server stopped gracefully")
}
