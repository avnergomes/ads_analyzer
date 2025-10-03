"""
Script de Aplicação Automática de Correções
============================================
Este script aplica automaticamente as correções necessárias no optimized-ads-analyzer.py

Uso:
    python apply_fixes.py
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


def backup_file(filepath):
    """Cria backup do arquivo original"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path


def apply_fixes():
    """Aplica as correções no arquivo"""
    
    file_path = Path(__file__).parent / "optimized-ads-analyzer.py"
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    print(f"📂 Aplicando correções em: {file_path}")
    
    # Criar backup
    backup_file(file_path)
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # ========== CORREÇÃO 1: Adicionar import ==========
    print("🔧 Aplicando Correção 1: Adicionando imports...")
    
    import_pattern = r'(from public_sheets_connector import PublicSheetsConnector)'
    import_addition = r'\1\nfrom data_mapper import DataMapper, integrate_sales_and_ads_data, safe_numeric'
    
    if 'from data_mapper import' not in content:
        content = re.sub(import_pattern, import_addition, content)
        print("   ✅ Import adicionado")
    else:
        print("   ⏭️  Import já existe")
    
    # ========== CORREÇÃO 2: Adicionar função safe_numeric_local ==========
    print("🔧 Aplicando Correção 2: Adicionando tratamento robusto de valores...")
    
    # Localizar o início da função render_show_health
    render_health_pattern = r'(latest = show_records\.iloc\[-1\]\s+funnel = funnel_summary\.get\(selected_show\))'
    
    safe_numeric_code = r'''\1
        
        # ============ CORREÇÃO DO ERRO - Tratamento robusto de valores ============
        def safe_numeric_local(value, default=0):
            """Converte valor para numérico de forma segura."""
            if pd.isna(value) or value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Extrair valores com tratamento seguro
        capacity = safe_numeric_local(latest.get('capacity', 0))
        remaining = safe_numeric_local(latest.get('remaining', 0))
        total_sold = safe_numeric_local(latest.get('total_sold', 0))
        today_sold = safe_numeric_local(latest.get('today_sold', 0))
        sales_to_date = safe_numeric_local(latest.get('sales_to_date', 0))
        avg_ticket_price = safe_numeric_local(latest.get('avg_ticket_price', 0))
        days_to_show = safe_numeric_local(latest.get('days_to_show', 1))
        avg_sales_last_7_days = safe_numeric_local(latest.get('avg_sales_last_7_days', 0))'''
    
    if 'safe_numeric_local' not in content:
        content = re.sub(render_health_pattern, safe_numeric_code, content)
        print("   ✅ Função safe_numeric_local adicionada")
    else:
        print("   ⏭️  Função já existe")
    
    # ========== CORREÇÃO 3: Substituir latest.get() por variáveis ==========
    print("🔧 Aplicando Correção 3: Substituindo acessos diretos a latest.get()...")
    
    replacements = [
        (r'int\(latest\.get\([\'"]capacity[\'"],[^)]*\)\)', 'int(capacity)'),
        (r'int\(latest\.get\([\'"]remaining[\'"],[^)]*\)\)', 'int(remaining)'),
        (r'int\(latest\.get\([\'"]total_sold[\'"],[^)]*\)\)', 'int(total_sold)'),
        (r'int\(latest\.get\([\'"]today_sold[\'"],[^)]*\)\)', 'int(today_sold)'),
        (r'latest\.get\([\'"]sales_to_date[\'"],[^)]*\)', 'sales_to_date'),
        (r'latest\.get\([\'"]avg_ticket_price[\'"],[^)]*\)', 'avg_ticket_price'),
        (r'latest\.get\([\'"]days_to_show[\'"],[^)]*\)', 'days_to_show'),
        (r'latest\.get\([\'"]avg_sales_last_7_days[\'"],[^)]*\)', 'avg_sales_last_7_days'),
        (r'latest\.get\([\'"]remaining[\'"],[^)]*\)\s*/\s*max\(latest\.get\([\'"]days_to_show[\'"][^)]*\)', 'remaining / max(days_to_show'),
        (r'latest\[[\'"]total_sold[\'"]\]', 'total_sold'),
    ]
    
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
    
    print("   ✅ Substituições aplicadas")
    
    # ========== CORREÇÃO 4: Corrigir lambda functions ==========
    print("🔧 Aplicando Correção 4: Corrigindo lambda functions em gráficos...")
    
    # Padrão para encontrar lambdas com comparações diretas
    lambda_pattern = r'lambda\s+x:\s+"#[0-9a-fA-F]{6}"\s+if\s+x\s+([><=]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    
    def fix_lambda(match):
        operator = match.group(1)
        variable = match.group(2)
        # Extrair a cor e o resto da expressão
        full_text = match.group(0)
        return full_text.replace('if x ', 'if safe_numeric_local(x) ')
    
    content = re.sub(lambda_pattern, fix_lambda, content)
    print("   ✅ Lambda functions corrigidas")
    
    # ========== CORREÇÃO 5: Adicionar Data Mapper section ==========
    print("🔧 Aplicando Correção 5: Adicionando seção de Data Mapper...")
    
    footer_pattern = r'(\s+# Footer\s+st\.markdown\("---"\))'
    
    data_mapper_section = r'''
    # Data Mapper e Qualidade
    if st.session_state.get("sales_data") is not None and len(dashboard.ads_data_by_type) > 0:
        with st.expander("🔗 Mapeamento de Dados - Qualidade e Integração"):
            st.markdown("### Relatório de Qualidade dos Dados")
            
            mapper = DataMapper()
            
            # Validar Sales
            st.markdown("#### 📊 Dados de Vendas (Google Sheets)")
            sales_quality = mapper.validate_data_quality(
                st.session_state["sales_data"], 
                'sales'
            )
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Linhas", sales_quality['row_count'])
            col2.metric("Colunas", sales_quality['column_count'])
            col3.metric("Qualidade", "✅ Válido" if sales_quality['valid'] else "❌ Inválido")
            
            if sales_quality['warnings']:
                st.warning("\\n".join(sales_quality['warnings']))
            
            # Validar Ads
            if 'days' in dashboard.ads_data_by_type:
                st.markdown("#### 📈 Dados de Anúncios (Meta)")
                ads_quality = mapper.validate_data_quality(
                    dashboard.ads_data_by_type['days'],
                    'ads'
                )
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Linhas", ads_quality['row_count'])
                col2.metric("Colunas", ads_quality['column_count'])
                col3.metric("Qualidade", "✅ Válido" if ads_quality['valid'] else "❌ Inválido")
                
                if ads_quality['warnings']:
                    st.warning("\\n".join(ads_quality['warnings']))
            
            # Integração
            st.markdown("### 🔄 Integração de Dados")
            
            if st.button("Executar Integração Avançada"):
                with st.spinner("Integrando dados..."):
                    integrated, stats = integrate_sales_and_ads_data(
                        st.session_state["sales_data"],
                        dashboard.ads_data_by_type.get('days'),
                        dashboard.ads_data_by_type.get('days_placement_device'),
                        dashboard.ads_data_by_type.get('days_time')
                    )
                    
                    # Mostrar estatísticas
                    st.success("✅ Integração concluída!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Shows Total", stats['total_shows'])
                    col2.metric("Shows Matched", stats['matched_shows'])
                    col3.metric("Shows Unmatched", stats['unmatched_shows'])
                    if stats['total_shows'] > 0:
                        col4.metric("Taxa de Match", f"{(stats['matched_shows']/stats['total_shows']*100):.1f}%")
                    
                    # Mostrar preview
                    st.markdown("#### Preview dos Dados Integrados")
                    st.dataframe(integrated.head(20), use_container_width=True)
                    
                    # Opção de download
                    csv = integrated.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Dados Integrados (CSV)",
                        data=csv,
                        file_name="integrated_sales_ads_data.csv",
                        mime="text/csv"
                    )
    
\1'''
    
    if 'Data Mapper e Qualidade' not in content:
        content = re.sub(footer_pattern, data_mapper_section + r'\1', content)
        print("   ✅ Seção Data Mapper adicionada")
    else:
        print("   ⏭️  Seção já existe")
    
    # ========== Verificar se houve mudanças ==========
    if content == original_content:
        print("\n⚠️  Nenhuma mudança foi necessária (arquivo já está corrigido ou padrões não encontrados)")
        return False
    
    # ========== Salvar arquivo corrigido ==========
    print("\n💾 Salvando arquivo corrigido...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo corrigido salvo em: {file_path}")
    
    return True


def main():
    """Função principal"""
    print("="*60)
    print("   Script de Aplicação Automática de Correções")
    print("   Ads Analyzer v4.0 → v4.1")
    print("="*60)
    print()
    
    try:
        if apply_fixes():
            print("\n" + "="*60)
            print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
            print("="*60)
            print("\n📋 Próximos passos:")
            print("   1. Revise as mudanças no arquivo optimized-ads-analyzer.py")
            print("   2. Execute: streamlit run optimized-ads-analyzer.py")
            print("   3. Teste o dashboard com seus dados")
            print("\n💡 Um backup do arquivo original foi criado")
        else:
            print("\n" + "="*60)
            print("⚠️  NENHUMA CORREÇÃO APLICADA")
            print("="*60)
            print("\n📋 Possíveis razões:")
            print("   - Arquivo já está corrigido")
            print("   - Padrões de código não encontrados")
            print("   - Verifique manualmente usando PATCH_INSTRUCTIONS.txt")
    
    except Exception as e:
        print(f"\n❌ Erro ao aplicar correções: {e}")
        print("\n📋 Use PATCH_INSTRUCTIONS.txt para aplicar manualmente")
        return False


if __name__ == "__main__":
    main()
