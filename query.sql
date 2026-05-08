-- Tổng quan doanh thu theo tháng
SELECT 
    d.month,
    SUM(f.total_amount) AS total_revenue
FROM 
    warehouse.fact_orders f
JOIN 
    warehouse.dim_dates d ON f.order_date_key = d.date_key
GROUP BY 
    d.month
ORDER BY 
    d.month;

-- Số Lượng Đơn Hàng Theo Trạng Thái
SELECT 
    f.order_status,
    COUNT(f.order_id) AS order_count
FROM 
    warehouse.fact_orders f
GROUP BY 
    f.order_status
ORDER BY 
    order_count DESC;

-- Số Lượng Sản Phẩm Bán Ra Theo Danh Mục
SELECT 
    p.product_category_name,
    count(f.order_id) AS total_sold
FROM 
    warehouse.fact_orders f
JOIN 
    warehouse.dim_products p ON f.product_key = p.product_id 
GROUP BY 
    p.product_category_name
ORDER BY 
    total_sold DESC;

-- doanh thu theo khu vuc
SELECT 
    g.geolocation_city,
    SUM(f.total_amount) AS total_revenue
FROM 
    warehouse.fact_orders f
JOIN 
    warehouse.dim_geolocation g ON f.geolocation_key = g.geolocation_key
GROUP BY 
    g.geolocation_city
ORDER BY 
    total_revenue DESC;

-- Mart: doanh thu theo ngay
SELECT
    order_date,
    order_count,
    total_revenue,
    average_order_value
FROM mart.mart_sales_daily
ORDER BY order_date;

-- Mart: top san pham theo doanh thu
SELECT
    product_id,
    product_category_name_english,
    total_quantity,
    total_revenue
FROM mart.mart_product_performance
ORDER BY total_revenue DESC
LIMIT 20;

-- Mart: doanh thu theo thanh pho
SELECT
    geolocation_city,
    geolocation_state,
    order_count,
    total_revenue
FROM mart.mart_city_revenue
ORDER BY total_revenue DESC
LIMIT 20;
