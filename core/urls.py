from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',   views.AlphaLoginView.as_view(), name='login'),
    path('logout/',  views.logout_view,               name='logout'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Products
    path('phong/',              views.ProductListView.as_view(),   name='product_list'),
    path('phong/<int:pk>/',     views.ProductDetailView.as_view(), name='product_detail'),
    path('phong/<int:pk>/chot-sale/', views.SaleFormView.as_view(), name='sale_form'),

    # Product CRUD (Manager)
    path('quan-ly/phong/',              views.ProductManageView.as_view(), name='product_manage'),
    path('quan-ly/phong/them/',         views.ProductManageView.as_view(), name='product_create'),
    path('quan-ly/phong/<int:pk>/sua/', views.ProductManageView.as_view(), name='product_edit'),
    path('quan-ly/phong/<int:pk>/xoa/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('quan-ly/phong/bulk/',         views.ProductBulkActionView.as_view(), name='product_bulk_action'),

    # Contracts (Staff & Manager)
    path('hop-dong/',                              views.ContractListView.as_view(),   name='contract_list'),
    path('hop-dong/<int:pk>/',                     views.ContractDetailView.as_view(), name='contract_detail'),
    path('hop-dong/<int:pk>/sua/',                 views.ContractEditView.as_view(),   name='contract_edit'),
    path('hop-dong/<int:pk>/duyet/',               views.ContractApproveView.as_view(), name='contract_approve'),
    path('hop-dong/<int:pk>/tu-choi/',             views.ContractRejectView.as_view(), name='contract_reject'),
    path('hop-dong/<int:pk>/huy-duyet/',           views.ContractCancelApproveView.as_view(), name='contract_cancel_approve'),
    path('hop-dong/<int:pk>/xoa/',                 views.ContractDeleteView.as_view(), name='contract_delete'),
    path('quan-ly/hop-dong/bulk/',                 views.ContractBulkActionView.as_view(), name='contract_bulk_action'),

    # Report & Map
    path('bao-cao/', views.ReportView.as_view(), name='report'),
    path('ban-do/', views.MapView.as_view(), name='map'),

    # Account Management (Manager)
    path('quan-ly/tai-khoan/',              views.AccountListView.as_view(),   name='account_list'),
    path('quan-ly/tai-khoan/them/',         views.AccountCreateView.as_view(), name='account_create'),
    path('quan-ly/tai-khoan/<int:pk>/xoa/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('quan-ly/tai-khoan/<int:pk>/sua/', views.AccountEditView.as_view(),   name='account_edit'),

    # Profile & Security
    path('ho-so/',        views.ProfileView.as_view(),            name='profile'),
    path('doi-mat-khau/', views.AlphaPasswordChangeView.as_view(), name='password_change'),
]
