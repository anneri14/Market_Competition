from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from services.products_generator import product_generator
from app import templates

router = APIRouter()

@router.get("/random")
async def get_random_product():
    """Возвращает один случайный товар"""
    try:
        return {
            "product": product_generator.get_random_product(),
            "source": "API" if product_generator._initialized else "default"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/all")
async def get_all_products():
    """Возвращает весь список товаров"""
    try:
        # Принудительно инициализируем при первом запросе
        if not product_generator._initialized:
            product_generator._initialize_products()
            
        return {
            "products": product_generator.products,
            "count": len(product_generator.products),
            "source": "API" if product_generator._initialized else "default"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
